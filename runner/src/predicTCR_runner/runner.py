from __future__ import annotations

import requests
import time
import logging
import os
import tempfile
import shutil
import subprocess


class Runner:
    def __init__(self, api_url: str, jwt_token: str, poll_interval: int = 5):
        self.api_url = api_url
        self.auth_header = {"Authorization": f"Bearer {jwt_token}"}
        self.poll_interval = poll_interval
        self.runner_hostname = os.environ.get("HOSTNAME", "unknown")
        self.logger = logging.getLogger(__name__)
        self.job_id: int | None = None
        self.sample_id: int | None = None

    def _request_job(self) -> bool:
        self.logger.debug(f"Requesting job from {self.api_url}...")
        self.job_id = None
        self.sample_id = None
        response = requests.post(
            url=f"{self.api_url}/runner/request_job",
            json={"runner_hostname": self.runner_hostname},
            headers=self.auth_header,
            timeout=30,
        )
        if response.status_code == 204:
            self.logger.debug("  -> no job available.")
            return False
        elif response.status_code == 200:
            self.job_id = response.json().get("job_id", None)
            self.sample_id = response.json().get("sample_id", None)
            self.logger.debug(
                f"  -> job id {self.job_id} for sample id {self.sample_id}."
            )
            if self.job_id is not None and self.sample_id is not None:
                return True
        else:
            self.logger.error(
                f"request_job failed with {response.status_code}: {response.content}"
            )
            return False

    def _report_job_failed(self, message: str):
        self.logger.info(f"...job {self.job_id} failed for sample id {self.sample_id}.")
        response = requests.post(
            url=f"{self.api_url}/runner/result",
            data={
                "job_id": self.job_id,
                "sample_id": self.sample_id,
                "runner_id": self.runner_hostname,
                "success": "false",
                "error_message": message,
            },
            headers=self.auth_header,
            timeout=30,
        )
        if response.status_code != 200:
            self.logger.error(f"result with {response.status_code}: {response.content}")

    def _upload_result(self, result_file: str):
        self.logger.info(
            f"...job {self.job_id} finished for sample id {self.sample_id}, uploading {result_file}..."
        )
        with open(result_file) as result_file:
            response = requests.post(
                url=f"{self.api_url}/runner/result",
                files={"file": result_file},
                data={
                    "job_id": self.job_id,
                    "sample_id": self.sample_id,
                    "runner_hostname": self.runner_hostname,
                    "success": True,
                },
                headers=self.auth_header,
                timeout=30,
            )
            if response.status_code != 200:
                self.logger.error(f"Failed to upload result: {response.content}")

    def _run_job(self):
        self.logger.info(
            f"Starting job {self.job_id} for sample id {self.sample_id}..."
        )
        self.logger.debug("Downloading input files...")
        with tempfile.TemporaryDirectory(delete=False) as tmpdir:
            for input_file_type in ["h5", "csv"]:
                response = requests.post(
                    url=f"{self.api_url}/input_{input_file_type}_file",
                    json={"sample_id": self.sample_id},
                    headers=self.auth_header,
                    timeout=30,
                )
                if response.status_code != 200:
                    self.logger.error(
                        f"Failed to download {input_file_type}: {response.content}"
                    )
                    return self._report_job_failed(
                        f"Failed to download {input_file_type} on {self.runner_hostname}",
                    )
                input_file_name = f"input.{input_file_type}"
                self.logger.debug(f"  - writing {input_file_name} to {tmpdir}...")
                with open(f"{tmpdir}/{input_file_name}", "wb") as input_file:
                    input_file.write(response.content)
            try:
                self.logger.debug(
                    f"  - copying contents of scripts folder to {tmpdir}..."
                )
                shutil.copytree("scripts", tmpdir, dirs_exist_ok=True)
                self.logger.debug(f"  - running {tmpdir}/scripts.sh...")
                subprocess.run(["sh", "./script.sh"], cwd=tmpdir, check=True)
                self.logger.debug(f"     ...{tmpdir}/script.sh finished.")
                self._upload_result(f"{tmpdir}/result.zip")
            except Exception as e:
                self.logger.exception(e)
                self.logger.error(
                    f"Failed to run job {self.job_id} for sample {self.sample_id}: {e}"
                )
                return self._report_job_failed(
                    f"Error during job execution on {self.runner_hostname}: {e}",
                )

    def start(self):
        self.logger.info(f"Polling {self.api_url} for jobs...")
        while True:
            if self._request_job():
                self._run_job()
            else:
                time.sleep(self.poll_interval)
