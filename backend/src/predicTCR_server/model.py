from __future__ import annotations

import re
import flask
from enum import Enum
import argon2
import pathlib
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from dataclasses import dataclass
from predicTCR_server.email import send_email
from predicTCR_server.settings import (
    predicTCR_url,
    predicTCR_submission_interval_minutes,
    predicTCR_submission_quota,
)
from predicTCR_server.logger import get_logger
from predicTCR_server.utils import (
    timestamp_now,
    encode_activation_token,
    decode_activation_token,
    encode_password_reset_token,
    decode_password_reset_token,
)

db = SQLAlchemy()
ph = argon2.PasswordHasher()
logger = get_logger()


class Status(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Sample(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(256), nullable=False)
    name: str = db.Column(db.String(128), nullable=False)
    tumor_type: str = db.Column(db.String(128), nullable=False)
    source: str = db.Column(db.String(128), nullable=False)
    timestamp: int = db.Column(db.Integer, nullable=False)
    status: Status = db.Column(db.Enum(Status), nullable=False)
    has_results_zip: bool = db.Column(db.Boolean, nullable=False)

    def _base_path(self) -> pathlib.Path:
        data_path = flask.current_app.config["PREDICTCR_DATA_PATH"]
        return pathlib.Path(f"{data_path}/{self.id}")

    def input_h5_file_path(self) -> pathlib.Path:
        return self._base_path() / "input.h5"

    def input_csv_file_path(self) -> pathlib.Path:
        return self._base_path() / "input.csv"

    def result_file_path(self) -> pathlib.Path:
        return self._base_path() / "result.zip"


@dataclass
class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.Text, nullable=False, unique=True)
    password_hash: str = db.Column(db.Text, nullable=False)
    activated: bool = db.Column(db.Boolean, nullable=False)
    enabled: bool = db.Column(db.Boolean, nullable=False)
    quota: int = db.Column(db.Integer, nullable=False)
    submission_interval_minutes: int = db.Column(db.Integer, nullable=False)
    last_submission_timestamp: int = db.Column(db.Integer, nullable=False)
    is_admin: bool = db.Column(db.Boolean, nullable=False)
    is_runner: bool = db.Column(db.Boolean, nullable=False)
    full_results: bool = db.Column(db.Boolean, nullable=False)

    def set_password_nocheck(self, new_password: str):
        self.password_hash = ph.hash(new_password)
        db.session.commit()

    def set_password(self, current_password: str, new_password: str) -> bool:
        if self.check_password(current_password):
            self.set_password_nocheck(new_password)
            return True
        return False

    def check_password(self, password: str) -> bool:
        try:
            ph.verify(self.password_hash, password)
        except argon2.exceptions.VerificationError:
            return False
        if ph.check_needs_rehash(self.password_hash):
            self.password_hash = ph.hash(password)
            db.session.commit()
        return True

    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "activated": self.activated,
            "enabled": self.enabled,
            "quota": self.quota,
            "submission_interval_minutes": self.submission_interval_minutes,
            "last_submission_timestamp": self.last_submission_timestamp,
            "is_admin": self.is_admin,
            "is_runner": self.is_runner,
            "full_results": self.full_results,
        }


def get_samples(email: str | None = None) -> list[Sample]:
    selected_samples = db.select(Sample).order_by(db.desc("timestamp"))
    if email is not None:
        selected_samples = selected_samples.filter(Sample.email == email)
    return db.session.execute(selected_samples).scalars().all()


def request_job() -> int | None:
    # todo: go through running jobs and reset to queued if they have been running for more than e.g. 2 hrs
    selected_samples = (
        db.select(Sample)
        .filter(Sample.status == Status.QUEUED)
        .order_by(db.asc("timestamp"))
    )
    sample = db.session.execute(selected_samples).scalars().first()
    if sample is None:
        logger.debug(" --> no samples in queue")
        return None
    else:
        logger.info(f"  --> sample id {sample.id}")
        sample.status = Status.RUNNING
        db.session.commit()
        return sample.id


def process_result(
    sample_id: str, success: bool, result_zip_file: FileStorage | None
) -> tuple[str, int]:
    sample = db.session.execute(
        db.select(Sample).filter_by(id=sample_id)
    ).scalar_one_or_none()
    if sample is None:
        logger.warning(f" --> Unknown sample id {sample_id}")
        return f"Unknown sample id {sample_id}", 400
    if success is False:
        sample.has_results_zip = False
        sample.status = Status.FAILED
        db.session.commit()
        return "Result processed", 200
    if result_zip_file is None:
        logger.warning(" --> No zipfile")
        return "Zip file missing", 400
    sample.result_file_path().parent.mkdir(parents=True, exist_ok=True)
    result_zip_file.save(sample.result_file_path())
    sample.has_results_zip = True
    sample.status = Status.COMPLETED
    db.session.commit()
    return "Result processed", 200


def is_valid_email(email: str) -> bool:
    return re.match(r"\S+@\S+\.\S+$", email) is not None


def is_valid_password(password: str) -> bool:
    return re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$", password) is not None


def _send_activation_email(email: str):
    secret_key = flask.current_app.config["JWT_SECRET_KEY"]
    token = encode_activation_token(email, secret_key)
    url = f"https://{predicTCR_url}/activate/{token}"
    logger.info(f"Activation url: {url}")
    msg_body = (
        f"To activate your predicTCR account,"
        f"please confirm your email address by clicking on the following link:\n\n"
        f"{url}\n\n"
        f"If you did not sign up for an account please disregard this email."
    )
    send_email(email, "predicTCR account activation", msg_body)


def send_password_reset_email(email: str) -> tuple[str, int]:
    user = db.session.execute(
        db.select(User).filter(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        logger.info(f"  -> Unknown email address '{email}'")
        msg_body = (
            "A password reset request was made for this email address, "
            "but no predicTCR account was found for this address.\n\n"
            "Maybe you signed up with a different email address?\n\n"
            "If you did not make this password reset request please disregard this email."
        )
    else:
        secret_key = flask.current_app.config["JWT_SECRET_KEY"]
        token = encode_password_reset_token(email, secret_key)
        url = f"https://{predicTCR_url}/reset_password/{token}"
        logger.info(f"Password reset url: {url}")
        msg_body = (
            f"To reset the password for your predicTCR account, "
            f"please click on the following link (valid for 1 hour):\n\n"
            f"{url}\n\n"
            f"If you did not make this password reset request please disregard this email."
        )
    send_email(email, "predicTCR password reset", msg_body)
    return f"Sent password reset email to '{email}'", 200


def add_new_user(email: str, password: str, is_admin: bool) -> tuple[str, int]:
    if not is_valid_email(email):
        return "Please enter a valid email address.", 400
    if not is_valid_password(password):
        return (
            "Password must contain at least 8 characters, including lower-case, upper-case and a number",
            400,
        )
    if (
        db.session.execute(
            db.select(User).filter(User.email == email)
        ).scalar_one_or_none()
        is not None
    ):
        return (
            "This email address is already in use",
            400,
        )
    try:
        _send_activation_email(email)
    except Exception as e:
        logger.warning(f"Send activation email failed: {e}")
        return "Failed to send activation email", 400
    try:
        db.session.add(
            User(
                email=email,
                password_hash=ph.hash(password),
                activated=False,
                enabled=False,
                quota=predicTCR_submission_quota,
                submission_interval_minutes=predicTCR_submission_interval_minutes,
                last_submission_timestamp=0,
                is_admin=is_admin,
                is_runner=False,
                full_results=False,
            )
        )
        db.session.commit()
    except Exception as e:
        logger.warning(f"Error adding user to db: {e}")
        return "Failed to create new user", 400
    return (
        f"Successful signup for {email}. To activate your account, please click on the link in the activation email from no-reply@{predicTCR_url} sent to this email address",
        200,
    )


def add_new_runner_user() -> User | None:
    try:
        runner_number = 1
        runner_name = f"runner{runner_number}"
        while (
            db.session.execute(
                db.select(User).filter(User.email == runner_name)
            ).scalar_one_or_none()
            is not None
        ):
            runner_number += 1
            runner_name = f"runner{runner_number}"
        db.session.add(
            User(
                email=runner_name,
                password_hash="",
                activated=False,
                enabled=True,
                quota=0,
                submission_interval_minutes=0,
                last_submission_timestamp=0,
                is_admin=False,
                is_runner=True,
                full_results=False,
            )
        )
        db.session.commit()
        return db.session.execute(
            db.select(User).filter(User.email == runner_name)
        ).scalar_one_or_none()
    except Exception as e:
        logger.warning(f"Error adding runner user: {e}")
        logger.exception(e)
        return None


def update_user(user_updates: dict) -> tuple[str, int]:
    email = user_updates.get("email", "")
    logger.info(f"Updating user {email}")
    user = db.session.execute(
        db.select(User).filter(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        logger.info(f"  -> Unknown email address '{email}'")
        return f"Unknown email address {email}", 404
    for key in [
        "enabled",
        "activated",
        "quota",
        "full_results",
        "submission_interval_minutes",
    ]:
        value = user_updates.get(key, None)
        if value is not None:
            setattr(user, key, value)
    db.session.commit()
    return f"Account {email} updated", 200


def activate_user(token: str) -> tuple[str, int]:
    logger.info("Activation request")
    secret_key = flask.current_app.config["JWT_SECRET_KEY"]
    email = decode_activation_token(token, secret_key)
    if email is None:
        logger.info("  -> Invalid token")
        return "Invalid or expired activation link", 400
    logger.info(f"  -> email '{email}'")
    user = db.session.execute(
        db.select(User).filter(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        logger.info(f"  -> Unknown email address '{email}'")
        return f"Unknown email address {email}", 400
    if user.activated is True:
        logger.info(f"  -> User with email {email} already activated")
        return f"Account for {email} is already activated", 400
    user.activated = True
    db.session.commit()
    return f"Account {email} activated", 200


def reset_user_password(token: str, email: str, new_password: str) -> tuple[str, int]:
    logger.info(f"Password reset request for {email}")
    secret_key = flask.current_app.config["JWT_SECRET_KEY"]
    decoded_email = decode_password_reset_token(token, secret_key)
    if decoded_email is None:
        logger.info("  -> Invalid token")
        return "Invalid or expired password reset link", 400
    logger.info(f"  -> decoded_email '{email}'")
    if email.lower() != decoded_email.lower():
        logger.info(
            f"  -> Supplied email '{email}' doesn't match decoded one '{decoded_email}'"
        )
        return "Invalid email address", 400
    user = db.session.execute(
        db.select(User).filter(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        logger.info(f"  -> Unknown email address '{email}'")
        return f"Unknown email address {email}", 400
    user.set_password_nocheck(new_password)
    db.session.commit()
    logger.info(f"  -> Password changed for {email}")
    return "Password changed", 200


def get_user_if_allowed_to_submit(email: str) -> tuple[User | None, str]:
    logger.info(f"Checking if {email} can submit a job")
    user = db.session.execute(
        db.select(User).filter(User.email == email)
    ).scalar_one_or_none()
    if user is None:
        return None, f"Unknown email address {email}."
    if user.quota <= 0:
        return None, "You have reached your sample submission quota."
    mins_since_last_submission = (
        timestamp_now() - user.last_submission_timestamp
    ) // 60
    logger.debug(
        f"{mins_since_last_submission}mins since last submission at {user.last_submission_timestamp}"
    )
    wait_time_mins = user.submission_interval_minutes - mins_since_last_submission
    logger.debug(f"Submission interval: {user.submission_interval_minutes}mins")
    logger.debug(f"  -> wait time: {wait_time_mins}min")
    if wait_time_mins > 0:
        return (
            None,
            f"Your next sample submission is available in {wait_time_mins} minute{'s' if wait_time_mins > 1 else ''}.",
        )
    return user, ""


def add_new_sample(
    email: str,
    name: str,
    tumor_type: str,
    source: str,
    h5_file: FileStorage,
    csv_file: FileStorage,
) -> tuple[Sample | None, str]:
    user, msg = get_user_if_allowed_to_submit(email)
    if user is None:
        return None, msg
    user.last_submission_timestamp = timestamp_now()
    user.quota -= 1
    new_sample = Sample(
        email=email,
        name=name,
        tumor_type=tumor_type,
        source=source,
        timestamp=timestamp_now(),
        status=Status.QUEUED,
        has_results_zip=False,
    )
    db.session.add(new_sample)
    db.session.commit()
    new_sample.input_h5_file_path().parent.mkdir(parents=True, exist_ok=True)
    h5_file.save(new_sample.input_h5_file_path())
    csv_file.save(new_sample.input_csv_file_path())
    return new_sample, ""
