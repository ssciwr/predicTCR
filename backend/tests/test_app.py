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


def _upload_result(client, result_zipfile: pathlib.Path, sample_id: int):
    headers = _get_auth_headers(client, "runner@abc.xy", "runner")
    with open(result_zipfile, "rb") as f:
        response = client.post(
            "/api/runner/result",
            data={
                "sample_id": sample_id,
                "success": True,
                "file": (io.BytesIO(f.read()), result_zipfile.name),
            },
            headers=headers,
        )
    return response


def test_result_valid(client, result_zipfile):
    headers = _get_auth_headers(client, "user@abc.xy", "user")
    sample_id = 1
    assert _upload_result(client, result_zipfile, sample_id).status_code == 200
    response = client.post(
        "/api/result",
        json={"sample_id": sample_id},
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.data) > 1


def test_admin_samples_valid(client):
    headers = _get_auth_headers(client, "admin@abc.xy", "admin")
    response = client.get("/api/admin/samples", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 4


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


def test_runner_result_valid(client, result_zipfile):
    response = _upload_result(client, result_zipfile, 1)
    assert response.status_code == 200
    assert "result processed" in response.json["message"].lower()
