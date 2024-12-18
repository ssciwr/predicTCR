from __future__ import annotations

import requests
import time
import logging
import pathlib
import os
import tempfile
import shutil
import subprocess


class Runner:
    def __init__(self, api_url: str, jwt_token: str, max_poll_interval: int = 60):
        self.api_url = api_url
        self.auth_header = {"Authorization": f"Bearer {jwt_token}"}
        self.max_poll_interval = max_poll_interval
        self.poll_interval = 1
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
            self.poll_interval = min(2 * self.poll_interval, self.max_poll_interval)
            self.logger.debug(
                f"  -> no job available, will check again in {self.poll_interval} seconds..."
            )
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

    def _report_job_failed(self, error_message: str):
        self.logger.info(f"...job {self.job_id} failed for sample id {self.sample_id}.")
        response = requests.post(
            url=f"{self.api_url}/runner/result",
            data={
                "job_id": self.job_id,
                "sample_id": self.sample_id,
                "runner_id": self.runner_hostname,
                "success": "false",
                "error_message": error_message,
            },
            headers=self.auth_header,
            timeout=30,
        )
        if response.status_code != 200:
            self.logger.error(f"result with {response.status_code}: {response.content}")

    def _upload_result(
        self,
        success: bool,
        user_results: str,
        trusted_user_results: str,
        admin_results: str,
        error_message: str,
    ):
        self.logger.info(
            f"...job {self.job_id} {'complete' if success else 'failed'} for sample id {self.sample_id}, uploading {user_results}, {trusted_user_results} and {admin_results}..."
        )
        with open(user_results, "rb") as user_result_file, open(
            trusted_user_results, "rb"
        ) as trusted_user_result_file, open(admin_results, "rb") as admin_result_file:
            response = requests.post(
                url=f"{self.api_url}/runner/result",
                files={
                    "user_results": user_result_file,
                    "trusted_user_results": trusted_user_result_file,
                    "admin_results": admin_result_file,
                },
                data={
                    "job_id": self.job_id,
                    "sample_id": self.sample_id,
                    "runner_hostname": self.runner_hostname,
                    "success": success,
                    "error_message": error_message,
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
                        f"Failed to download {input_file_type} on {self.runner_hostname}"
                    )
                input_file_name = f"input.{input_file_type}"
                self.logger.debug(f"  - writing {input_file_name} to {tmpdir}...")
                with open(f"{tmpdir}/{input_file_name}", "wb") as input_file:
                    input_file.write(response.content)
            try:
                result_folders = [
                    "admin_results",
                    "trusted_user_results",
                    "user_results",
                ]
                self.logger.debug(
                    f"  - copying contents of script folder to {tmpdir}..."
                )
                shutil.copytree("/script", tmpdir, dirs_exist_ok=True)
                self.logger.debug(
                    "  - making admin_results and user_results folders..."
                )
                for result_folder in result_folders:
                    (pathlib.Path(tmpdir) / result_folder).mkdir(exist_ok=True)
                self.logger.debug(f"  - running {tmpdir}/script.sh...")
                script_output_last_line = ""
                with subprocess.Popen(
                    args=["./script.sh"],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf-8",
                    universal_newlines=True,
                ) as proc:
                    for line in proc.stdout:
                        script_output_last_line = line.strip()
                        self.logger.debug(f"./script.sh :: {script_output_last_line}")
                success = proc.returncode == 0
                error_message = script_output_last_line if not success else ""
                self.logger.debug(
                    f"     ...{tmpdir}/script.sh {'finished' if success else 'failed'}."
                )
                for result_folder in result_folders:
                    result_folder_path = str(pathlib.Path(tmpdir) / result_folder)
                    shutil.make_archive(result_folder_path, "zip", result_folder_path)
                self._upload_result(
                    success=success,
                    admin_results=f"{tmpdir}/admin_results.zip",
                    trusted_user_results=f"{tmpdir}/trusted_user_results.zip",
                    user_results=f"{tmpdir}/user_results.zip",
                    error_message=error_message,
                )
                self.poll_interval = 1
            except Exception as e:
                self.logger.exception(e)
                self.logger.error(
                    f"Failed to run job {self.job_id} for sample {self.sample_id}: {e}"
                )
                return self._report_job_failed(
                    f"Error during job execution on {self.runner_hostname}: {e}"
                )

    def start(self):
        self.logger.info(f"Polling {self.api_url} for jobs...")
        while True:
            if self._request_job():
                self._run_job()
            else:
                time.sleep(self.poll_interval)
