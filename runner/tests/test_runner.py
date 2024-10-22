from predicTCR_runner.runner import Runner


def test_runner_request_job(requests_mock):
    requests_mock.post("http://api/runner/request_job", status_code=204)
    runner = Runner(api_url="http://api", jwt_token="abc")
    assert runner._request_job() is False
    requests_mock.post(
        "http://api/runner/request_job", json={"job_id": 22, "sample_id": 44}
    )
    assert runner._request_job() is True
