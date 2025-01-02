from __future__ import annotations

import re
import flask
import enum
import argon2
import pathlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column
from werkzeug.datastructures import FileStorage
from sqlalchemy.inspection import inspect
from sqlalchemy import Integer, String, Boolean, Enum
from dataclasses import dataclass
from predicTCR_server.email import send_email
from predicTCR_server.settings import predicTCR_url
from predicTCR_server.logger import get_logger
from predicTCR_server.utils import (
    timestamp_now,
    encode_activation_token,
    decode_activation_token,
    encode_password_reset_token,
    decode_password_reset_token,
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)
ph = argon2.PasswordHasher()
logger = get_logger()


class Status(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Settings(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_personal_submission_quota: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    default_personal_submission_interval_mins: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    global_quota: Mapped[int] = mapped_column(Integer, nullable=False)
    tumor_types: Mapped[str] = mapped_column(String, nullable=False)
    sources: Mapped[str] = mapped_column(String, nullable=False)
    platforms: Mapped[str] = mapped_column(String, nullable=False)
    csv_required_columns: Mapped[str] = mapped_column(String, nullable=False)
    runner_job_timeout_mins: Mapped[int] = mapped_column(Integer, nullable=False)
    max_filesize_h5_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    max_filesize_csv_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    about_md: Mapped[str] = mapped_column(String, nullable=False)

    def as_dict(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}


@dataclass
class Job(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[int] = mapped_column(Integer, nullable=False)
    runner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    runner_hostname: Mapped[str] = mapped_column(String, nullable=False)
    timestamp_start: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_end: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)

    def as_dict(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}


@dataclass
class Sample(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tumor_type: Mapped[str] = mapped_column(String(128), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    platform: Mapped[str] = mapped_column(String(128), nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_job_start: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_job_end: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    has_results_zip: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)

    def base_path(self) -> pathlib.Path:
        data_path = flask.current_app.config["PREDICTCR_DATA_PATH"]
        return pathlib.Path(f"{data_path}/{self.id}")

    def input_h5_file_path(self) -> pathlib.Path:
        return self.base_path() / "input.h5"

    def input_csv_file_path(self) -> pathlib.Path:
        return self.base_path() / "input.csv"

    def user_result_file_path(self) -> pathlib.Path:
        return self.base_path() / "user_results.zip"

    def trusted_user_result_file_path(self) -> pathlib.Path:
        return self.base_path() / "trusted_user_results.zip"

    def admin_result_file_path(self) -> pathlib.Path:
        return self.base_path() / "admin_results.zip"


@dataclass
class User(db.Model):
    id: int = mapped_column(Integer, primary_key=True)
    email: str = mapped_column(String, nullable=False, unique=True)
    password_hash: str = mapped_column(String, nullable=False)
    activated: bool = mapped_column(Boolean, nullable=False)
    enabled: bool = mapped_column(Boolean, nullable=False)
    quota: int = mapped_column(Integer, nullable=False)
    submission_interval_minutes: int = mapped_column(Integer, nullable=False)
    last_submission_timestamp: int = mapped_column(Integer, nullable=False)
    is_admin: bool = mapped_column(Boolean, nullable=False)
    is_runner: bool = mapped_column(Boolean, nullable=False)
    full_results: bool = mapped_column(Boolean, nullable=False)

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
            c: getattr(self, c)
            for c in inspect(self).attrs.keys()
            if c != "password_hash"
        }


def get_samples(email: str | None = None) -> list[Sample]:
    selected_samples = db.select(Sample).order_by(db.desc("timestamp"))
    if email is not None:
        selected_samples = selected_samples.filter(Sample.email == email)
    return db.session.execute(selected_samples).scalars().all()


def request_job() -> int | None:
    job_timeout_minutes = db.session.get(Settings, 1).runner_job_timeout_mins
    sample_to_resubmit = (
        db.session.execute(
            db.select(Sample).filter(
                (Sample.status == Status.RUNNING)
                & (
                    timestamp_now() - Sample.timestamp_job_start
                    > job_timeout_minutes * 60
                )
            )
        )
        .scalars()
        .first()
    )
    if sample_to_resubmit is not None:
        logger.info(
            f"Sample {sample_to_resubmit.id} has been running for more than {job_timeout_minutes} minutes - putting back in queue"
        )
        sample_to_resubmit.status = Status.QUEUED
        db.session.commit()
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
        sample.timestamp_job_start = timestamp_now()
        sample.timestamp_job_end = 0
        sample.status = Status.RUNNING
        db.session.commit()
        return sample.id


def process_result(
    job_id: int,
    sample_id: int,
    success: bool,
    error_message: str,
    user_result_zip_file: FileStorage | None,
    trusted_user_result_zip_file: FileStorage | None,
    admin_result_zip_file: FileStorage | None,
) -> tuple[str, int]:
    sample = db.session.get(Sample, sample_id)
    if sample is None:
        logger.warning(f" --> Unknown sample id {sample_id}")
        return f"Unknown sample id {sample_id}", 400
    sample.base_path().mkdir(parents=True, exist_ok=True)
    job = db.session.get(Job, job_id)
    if job is None:
        logger.warning(f" --> Unknown job id {job_id}")
        return f"Unknown job id {job_id}", 400
    sample.timestamp_job_end = timestamp_now()
    job.timestamp_end = timestamp_now()
    if success:
        job.status = Status.COMPLETED
        sample.error_message = ""
    else:
        job.status = Status.FAILED
        job.error_message = error_message
        sample.error_message = error_message
    db.session.commit()
    if sample.has_results_zip:
        logger.warning(f" --> Sample {sample_id} already has results")
        return f"Sample {sample_id} already has results", 400
    if admin_result_zip_file is not None:
        admin_result_zip_file.save(sample.admin_result_file_path())
    if success is False:
        sample.has_results_zip = False
        sample.status = Status.FAILED
        db.session.commit()
        return "Result processed", 200
    if user_result_zip_file is None or trusted_user_result_zip_file is None:
        logger.warning(" --> Missing user result zipfile")
        return "User result zip file missing", 400
    user_result_zip_file.save(sample.user_result_file_path())
    trusted_user_result_zip_file.save(sample.trusted_user_result_file_path())
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
                id=None,
                email=email,
                password_hash=ph.hash(password),
                activated=False,
                enabled=False,
                quota=db.session.get(Settings, 1).default_personal_submission_quota,
                submission_interval_minutes=db.session.get(
                    Settings, 1
                ).default_personal_submission_interval_mins,
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
                id=None,
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
    settings = db.session.get(Settings, 1)
    if settings.global_quota <= 0:
        return None, "The service has reached its sample submission quota."
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
    platform: str,
    h5_file: FileStorage,
    csv_file: FileStorage,
) -> tuple[Sample | None, str]:
    user, msg = get_user_if_allowed_to_submit(email)
    if user is None:
        return None, msg
    user.last_submission_timestamp = timestamp_now()
    user.quota -= 1
    settings = db.session.get(Settings, 1)
    settings.global_quota -= 1
    new_sample = Sample(
        id=None,
        email=email,
        name=name,
        tumor_type=tumor_type,
        source=source,
        platform=platform,
        timestamp=timestamp_now(),
        timestamp_job_start=0,
        timestamp_job_end=0,
        status=Status.QUEUED,
        has_results_zip=False,
        error_message="",
    )
    db.session.add(new_sample)
    db.session.commit()
    new_sample.input_h5_file_path().parent.mkdir(parents=True, exist_ok=True)
    h5_file.save(new_sample.input_h5_file_path())
    csv_file.save(new_sample.input_csv_file_path())
    return new_sample, ""
