from __future__ import annotations

import requests
import time
import logging
import click
import os
import tempfile
import shutil
import zipfile
import io
import subprocess


class Runner:
    def __init__(self, api_url: str, jwt_token: str, poll_interval: int = 5):
        self.api_url = api_url
        self.auth_header = {"Authorization": f"Bearer {jwt_token}"}
        self.poll_interval = poll_interval
        self.runner_hostname = os.environ.get("HOSTNAME", "unknown")
        self.logger = logging.getLogger(__name__)

    def _request_job(self) -> int | None:
        self.logger.debug(f"Requesting job from {self.api_url}...")
        response = requests.post(
            url=f"{self.api_url}/runner/request_job",
            json={"runner_hostname": self.runner_hostname},
            headers=self.auth_header,
            timeout=30,
        )
        if response.status_code == 204:
            self.logger.debug("  -> no job available.")
            return None
        elif response.status_code == 200:
            sample_id = response.json().get("sample_id", None)
            self.logger.debug(f"  -> sample id {sample_id} available.")
            return sample_id
        else:
            self.logger.error(
                f"request_job failed with {response.status_code}: {response.content}"
            )
            return None

    def _report_job_failed(self, sample_id: int, message: str):
        self.logger.info(f"...job failed for sample id {sample_id}.")
        response = requests.post(
            url=f"{self.api_url}/runner/result",
            data={
                "sample_id": sample_id,
                "runner_id": self.runner_hostname,
                "success": "false",
                "error_message": message,
            },
            headers=self.auth_header,
            timeout=30,
        )
        if response.status_code != 200:
            self.logger.error(f"result with {response.status_code}: {response.content}")

    def _upload_result(self, sample_id: int, result_file: str):
        self.logger.info(
            f"...job finished for sample id {sample_id}, uploading {result_file}..."
        )
        with open(result_file) as result_file:
            response = requests.post(
                url=f"{self.api_url}/runner/result",
                files={"file": result_file},
                data={
                    "sample_id": sample_id,
                    "runner_hostname": self.runner_hostname,
                    "success": True,
                },
                headers=self.auth_header,
                timeout=30,
            )
            if response.status_code != 200:
                self.logger.error(f"Failed to upload result: {response.content}")

    def _run_job(self, sample_id: int):
        self.logger.info(f"Starting job for sample id {sample_id}...")
        self.logger.debug("Downloading input file...")
        response = requests.post(
            url=f"{self.api_url}/input_file",
            json={"sample_id": sample_id},
            headers=self.auth_header,
            timeout=30,
        )
        if response.status_code != 200:
            self.logger.error(f"Failed to download input file: {response.content}")
            return self._report_job_failed(
                sample_id, f"Failed to download input file on {self.runner_hostname}"
            )
        with tempfile.TemporaryDirectory(delete=False) as tmpdir:
            try:
                zip_file = zipfile.ZipFile(io.BytesIO(response.content))
                self.logger.debug(
                    f"  - extracting {zip_file.namelist()} to {tmpdir}..."
                )
                zip_file.extractall(tmpdir)
                self.logger.debug(
                    f"  - copying contents of scripts folder to {tmpdir}..."
                )
                shutil.copytree("scripts", tmpdir, dirs_exist_ok=True)
                self.logger.debug(f"  - running {tmpdir}/scripts.sh...")
                subprocess.run(["sh", "./script.sh"], cwd=tmpdir, check=True)
                self.logger.debug(f"     ...{tmpdir}/script.sh finished.")
                self._upload_result(sample_id, f"{tmpdir}/result.zip")
            except Exception as e:
                self.logger.exception(e)
                self.logger.error(f"Failed to run job for sample {sample_id}: {e}")
                return self._report_job_failed(
                    sample_id,
                    f"Error during job execution on {self.runner_hostname}: {e}",
                )

    def start(self):
        self.logger.info(f"Polling {self.api_url} for jobs...")
        while True:
            job_id = self._request_job()
            if job_id is not None:
                self._run_job(job_id)
            else:
                time.sleep(self.poll_interval)


@click.command()
@click.option("--api-url", type=str)
@click.option("--jwt-token", type=str)
@click.option("--poll-interval", type=int, default=5, show_default=True)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="Log level",
    show_default=True,
    show_choices=True,
)
def main(api_url, jwt_token, poll_interval, log_level):
    logging.basicConfig(
        level=log_level, format="%(levelname)s %(module)s.%(funcName)s :: %(message)s"
    )
    runner = Runner(api_url, jwt_token, poll_interval)
    runner.start()


if __name__ == "__main__":
    main(auto_envvar_prefix="PREDICTCR")
