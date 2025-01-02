from __future__ import annotations
from typing import Dict
import io
import pytest
import pathlib
import predicTCR_server
import flask_test_utils as ftu


def _get_auth_headers(
    client, email: str = "user@abc.xy", password: str = "user"
) -> Dict:
    response = client.post("/api/login", json={"email": email, "password": password})
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_invalid(client):
    # missing json
    response = client.post("/api/login")
    assert response.status_code > 200
    # unknown email
    response = client.post("/api/login", json={"email": "", "password": ""})
    assert response.status_code == 400
    assert response.json["message"] == "Unknown email address"
    # wrong password
    response = client.post("/api/login", json={"email": "user@abc.xy", "password": ""})
    assert response.status_code == 400
    assert response.json["message"] == "Incorrect password"


def test_login_valid(client):
    email = "user@abc.xy"
    password = "user"
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["user"]["email"] == email
    assert response.json["user"]["is_admin"] is False


def test_change_password_invalid(client):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/login", json={"email": "user@abc.xy", "password": "user"}
    )
    assert response.status_code == 200
    response = client.post(
        "/api/change_password",
        headers=headers,
        json={"current_password": "wrong", "new_password": "abc123"},
    )
    assert response.status_code == 400
    assert "Failed to change password" in response.json["message"]
    response = client.post(
        "/api/change_password", headers=headers, json={"new_password": "abc123"}
    )
    assert response.status_code == 400
    assert response.json["message"] == "Current password missing"
    response = client.post(
        "/api/change_password", headers=headers, json={"current_password": "abc123"}
    )
    assert response.status_code == 400
    assert response.json["message"] == "New password missing"


def test_change_password_valid(client):
    headers = _get_auth_headers(client)
    response = client.post(
        "/api/login", json={"email": "user@abc.xy", "password": "user"}
    )
    assert response.status_code == 200
    response = client.post(
        "/api/change_password",
        headers=headers,
        json={"current_password": "user", "new_password": "abc123"},
    )
    assert response.status_code == 200
    assert "Password changed" in response.json["message"]
    response = client.post(
        "/api/login", json={"email": "user@abc.xy", "password": "user"}
    )
    assert response.status_code == 400
    response = client.post(
        "/api/login", json={"email": "user@abc.xy", "password": "abc123"}
    )
    assert response.status_code == 200


def test_jwt_same_secret_persists_valid_tokens(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "0123456789abcdefghijklmnopqrstuvwxyz")
    app1 = predicTCR_server.create_app(data_path=str(tmp_path))
    ftu.add_test_users(app1)
    client1 = app1.test_client()
    headers1 = _get_auth_headers(client1)
    assert client1.get("/api/samples", headers=headers1).status_code == 200
    # create new app with same JWT secret key & user database
    app2 = predicTCR_server.create_app(data_path=str(tmp_path))
    client2 = app2.test_client()
    # can re-use the same JWT token in the new app
    assert client2.get("/api/samples", headers=headers1).status_code == 200


def test_jwt_different_secret_invalidates_tokens(tmp_path, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "")  # too short: uses random one instead
    app1 = predicTCR_server.create_app(data_path=str(tmp_path))
    ftu.add_test_users(app1)
    client1 = app1.test_client()
    headers1 = _get_auth_headers(client1)
    assert client1.get("/api/samples", headers=headers1).status_code == 200
    # create new app with a different JWT secret key & user database
    monkeypatch.setenv("JWT_SECRET_KEY", "")  # too short: uses random one instead
    app2 = predicTCR_server.create_app(data_path=str(tmp_path))
    client2 = app2.test_client()
    # can't re-use the same JWT token in the new app
    assert client2.get("/api/samples", headers=headers1).status_code == 422


def test_samples_invalid(client):
    # no auth header
    response = client.get("/api/samples")
    assert response.status_code == 401


def test_samples_valid(client):
    headers = _get_auth_headers(client)
    response = client.get("/api/samples", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 4


def test_get_settings_valid(client):
    headers = _get_auth_headers(client)
    response = client.get("/api/settings", headers=headers)
    assert response.status_code == 200
    assert response.json == {
        "csv_required_columns": "barcode;cdr3;chain",
        "default_personal_submission_interval_mins": 30,
        "default_personal_submission_quota": 10,
        "global_quota": 1000,
        "id": 1,
        "sources": "TIL;PMBC;Other",
        "tumor_types": "Lung;Breast;Other",
        "platforms": "Illumina;Other",
        "runner_job_timeout_mins": 60,
        "max_filesize_h5_mb": 50,
        "max_filesize_csv_mb": 10,
        "about_md": "",
    }


def test_update_settings_valid(client):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    new_settings = {
        "csv_required_columns": "BB;CC;QQ",
        "default_personal_submission_interval_mins": 60,
        "default_personal_submission_quota": 7,
        "global_quota": 999,
        "id": 1,
        "sources": "a;b;g",
        "tumor_types": "1;2;6",
        "platforms": "Alpha;Beta;Other",
        "runner_job_timeout_mins": 12,
        "max_filesize_h5_mb": 77,
        "max_filesize_csv_mb": 12,
        "about_md": "# About",
        "invalid-key": "invalid",
    }
    response = client.post("/api/admin/settings", headers=headers, json=new_settings)
    assert response.status_code == 200
    new_settings.pop("invalid-key")
    assert client.get("/api/settings", headers=headers).json == new_settings


@pytest.mark.parametrize("input_file_type", ["h5", "csv"])
def test_input_file_invalid(client, input_file_type: str):
    # no auth header
    response = client.post(
        f"/api/input_{input_file_type}_file",
        json={"sample_id": 2},
    )
    assert response.status_code == 401
    # invalid sample id
    headers = _get_auth_headers(client)
    response = client.post(
        f"/api/input_{input_file_type}_file",
        json={"sample_id": 66},
        headers=headers,
    )
    assert response.status_code == 400
    assert "not found" in response.json["message"]


@pytest.mark.parametrize("input_file_type", ["h5", "csv"])
def test_input_file_valid(client, input_file_type: str):
    headers = _get_auth_headers(client)
    response = client.post(
        f"/api/input_{input_file_type}_file",
        json={"sample_id": 2},
        headers=headers,
    )
    assert response.status_code == 200
    with io.BytesIO(response.data) as f:
        assert input_file_type in f.read().decode("utf-8")


def test_result_invalid(client):
    response = client.post("/api/result", json={"sample_id": 66})
    assert response.status_code == 401
    headers = _get_auth_headers(client, "user@abc.xy", "user")
    response = client.post("/api/result", json={"sample_id": 66}, headers=headers)
    assert response.status_code == 400
    assert "Sample not found" in response.json["message"]
    response = client.post(
        "/api/result",
        json={"sample_id": 1},
        headers=headers,
    )
    assert response.status_code == 400
    assert "No results available" in response.json["message"]


def _upload_result(client, result_zipfile: pathlib.Path, job_id: int, sample_id: int):
    headers = _get_auth_headers(client, "runner@abc.xy", "runner")
    with open(result_zipfile, "rb") as f:
        response = client.post(
            "/api/runner/result",
            data={
                "job_id": job_id,
                "sample_id": sample_id,
                "success": True,
                "user_results": (io.BytesIO(f.read()), result_zipfile.name),
                "trusted_user_results": (io.BytesIO(f.read()), result_zipfile.name),
                "admin_results": (io.BytesIO(f.read()), result_zipfile.name),
            },
            headers=headers,
        )
    return response


def test_runner_valid_success(client, result_zipfile):
    headers = _get_auth_headers(client, "runner@abc.xy", "runner")
    # request job
    request_job_response = client.post(
        "/api/runner/request_job",
        json={"runner_hostname": "me"},
        headers=headers,
    )
    assert request_job_response.status_code == 200
    assert request_job_response.json == {"sample_id": 1, "job_id": 1}
    # upload successful result
    assert _upload_result(client, result_zipfile, 1, 1).status_code == 200
    response = client.post(
        "/api/result",
        json={"sample_id": 1},
        headers=_get_auth_headers(client, "user@abc.xy", "user"),
    )
    assert response.status_code == 200
    assert len(response.data) > 1


def test_runner_valid_failure(client, result_zipfile):
    headers = _get_auth_headers(client, "runner@abc.xy", "runner")
    # request job
    request_job_response = client.post(
        "/api/runner/request_job",
        json={"runner_hostname": "me"},
        headers=headers,
    )
    assert request_job_response.status_code == 200
    assert request_job_response.json == {"sample_id": 1, "job_id": 1}
    # upload failure result
    result_response = client.post(
        "/api/runner/result",
        data={
            "job_id": 1,
            "sample_id": 1,
            "success": False,
            "error_message": "Something went wrong",
        },
        headers=headers,
    )
    assert result_response.status_code == 200
    response = client.post(
        "/api/result",
        json={"sample_id": 1},
        headers=_get_auth_headers(client, "user@abc.xy", "user"),
    )
    assert response.status_code == 400


def test_admin_samples_valid(client):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    response = client.get("/api/admin/samples", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 4


def test_admin_delete_samples_valid_admin_user(client):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    assert len(client.get("/api/admin/samples", headers=headers).json) == 4
    response = client.delete("/api/admin/samples/1", headers=headers)
    assert response.status_code == 200
    assert len(client.get("/api/admin/samples", headers=headers).json) == 3
    response = client.delete("/api/admin/samples/1", headers=headers)
    assert response.status_code == 404
    response = client.delete("/api/admin/samples/2", headers=headers)
    assert response.status_code == 200
    assert len(client.get("/api/admin/samples", headers=headers).json) == 2


@pytest.mark.parametrize(
    "index,sample_id,status",
    [(0, 4, "failed"), (1, 3, "completed"), (2, 2, "running"), (3, 1, "queued")],
)
def test_admin_resubmit_samples_valid_admin_user(client, index, sample_id, status):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    sample_before = client.get("/api/admin/samples", headers=headers).json[index]
    assert sample_before["status"] == status
    response = client.post(f"/api/admin/resubmit-sample/{sample_id}", headers=headers)
    assert response.status_code == 200
    sample_after = client.get("/api/admin/samples", headers=headers).json[index]
    assert sample_after["status"] == "queued"
    assert sample_after["has_results_zip"] is False


def test_admin_runner_token_invalid(client):
    # no auth header
    response = client.get("/api/admin/runner_token")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/api/admin/runner_token", headers=headers)
    assert response.status_code == 400


@pytest.mark.parametrize("input_file_type", ["h5", "csv"])
def test_admin_runner_token_valid(client, input_file_type: str):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    response = client.get("/api/admin/runner_token", headers=headers)
    assert response.status_code == 200
    new_token = response.json["access_token"]
    assert (
        client.post(
            f"/api/input_{input_file_type}_file",
            json={"sample_id": 1},
            headers={"Authorization": f"Bearer {new_token}"},
        ).status_code
        == 200
    )


def test_admin_users_invalid(client):
    # no auth header
    response = client.get("/api/admin/users")
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 400


def test_admin_users_valid(client):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    response = client.get("/api/admin/users", headers=headers)
    assert response.status_code == 200
    assert "users" in response.json


def test_admin_update_user_valid(client):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    user = client.get("/api/admin/users", headers=headers).json["users"][0]
    invalid_update_keys = ["password", "idontexist"]
    for invalid_update_key in invalid_update_keys:
        user[invalid_update_key] = "this-will-be-ignored"
    user["enabled"] = False
    user["activated"] = False
    user["quota"] = 99
    user["full_results"] = True
    user["submission_interval_minutes"] = 17
    response = client.post("/api/admin/user", headers=headers, json=user)
    assert response.status_code == 200
    assert user["email"] in response.json["message"]
    assert "updated" in response.json["message"]
    updated_user = client.get("/api/admin/users", headers=headers).json["users"][0]
    for invalid_update_key in invalid_update_keys:
        user.pop(invalid_update_key)
    assert updated_user == user


def test_admin_update_user_invalid(client):
    user_update = {"email": "Idontexist", "quota": 42}
    # no auth header
    response = client.post("/api/admin/user", json=user_update)
    assert response.status_code == 401
    # valid non-admin user auth header
    headers = _get_auth_headers(client)
    response = client.post("/api/admin/user", headers=headers, json=user_update)
    assert response.status_code == 400
    # invalid user email
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    response = client.post("/api/admin/user", headers=headers, json=user_update)
    assert response.status_code == 404
