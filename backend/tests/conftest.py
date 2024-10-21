from __future__ import annotations

import pytest
from predicTCR_server import create_app
import shutil
import flask
import os
import sys
import pathlib
import smtplib

# add tests helpers package location to path so tests can import gui_test_utils
sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

import flask_test_utils as ftu


@pytest.fixture()
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET_KEY", "abcdefghijklmnopqrstuvwxyz")
    monkeypatch.setattr(
        smtplib.SMTP,
        "__init__",
        lambda self, host: print(f"Monkeypatched SMTP host: {host}", flush=True),
    )
    monkeypatch.setattr(
        smtplib.SMTP,
        "send_message",
        lambda self, msg: flask.current_app.config.update(
            TESTING_ONLY_LAST_SMTP_MESSAGE=msg
        ),
    )
    temp_data_path = str(tmp_path)
    app = create_app(data_path=temp_data_path)
    ftu.add_test_users(app)
    ftu.add_test_samples(app, tmp_path)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def result_zipfile(tmp_path) -> pathlib.Path:
    # make a results zip file with files a.txt, b.txt, c.txt, email.txt
    results_zipfile_contents = tmp_path / "results_zipfile"
    results_zipfile_contents.mkdir()
    result_files = ["a.txt", "b.txt", "c.txt"]
    for result_file in result_files:
        with open(results_zipfile_contents / result_file, "w") as f:
            f.write(f"test file named {result_file}")
    result_zipfile = pathlib.Path(
        shutil.make_archive(
            f"{tmp_path}/result_zipfile", "zip", results_zipfile_contents
        )
    )
    yield result_zipfile
