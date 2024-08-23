from __future__ import annotations

import logging
from typing import Optional, Dict, Tuple, List
import smtplib
from email.message import EmailMessage
import re
import flask
import zipfile
import shutil
import argon2
import tempfile
import pathlib
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from dataclasses import dataclass
from predicTCR_server.logger import get_logger
from predicTCR_server.utils import get_primary_key
from predicTCR_server.utils import get_start_of_week
import csv
from predicTCR_server.utils import (
    encode_activation_token,
    decode_activation_token,
    encode_password_reset_token,
    decode_password_reset_token,
)

db = SQLAlchemy()
ph = argon2.PasswordHasher()
logger = get_logger("predicTCRServer")


@dataclass
class Settings(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    datetime: datetime.datetime = db.Column(db.DateTime, nullable=False)
    email: str = db.Column(db.String(256), nullable=False)
    settings_dict: Dict = db.Column(db.PickleType, nullable=False)


def default_settings_dict() -> Dict:
    return {
        "plate_n_rows": 8,
        "plate_n_cols": 12,
        "running_options": ["dna_r9.4.1_450bps_sup.cfg", "dna_r9.4.1_480bps_sup.cfg"],
        "last_submission_day": 3,
    }


def get_current_settings() -> Dict:
    settings_tuple = db.session.execute(
        db.select(Settings).order_by(db.desc(Settings.id))
    ).first()
    if settings_tuple is not None:
        settings_dict = settings_tuple[0].settings_dict
        for key, value in default_settings_dict().items():
            # use default values for any missing keys
            if key not in settings_dict:
                settings_dict[key] = value
        return settings_dict
    # no settings in db: create default settings and add to db
    settings = Settings(
        datetime=datetime.datetime.today(),
        email="default",
        settings_dict=default_settings_dict(),
    )
    db.session.add(settings)
    db.session.commit()
    return settings.settings_dict


def set_current_settings(email: str, settings_dict: Dict) -> Tuple[str, int]:
    for required_field in default_settings_dict():
        if required_field not in settings_dict:
            return (
                f"Required field {required_field} missing - settings not updated",
                400,
            )
    settings = Settings(
        datetime=datetime.datetime.today(), email=email, settings_dict=settings_dict
    )
    db.session.add(settings)
    db.session.commit()
    return f"Settings updated by {settings.email} at {settings.datetime}", 200


@dataclass
class Sample(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(256), nullable=False)
    primary_key: str = db.Column(db.String(32), nullable=False, unique=True)
    tube_primary_key: str = db.Column(db.String(32), nullable=False)
    name: str = db.Column(db.String(128), nullable=False)
    running_option: str = db.Column(db.String(128), nullable=False)
    concentration: int = db.Column(db.Integer, nullable=False)
    date: datetime.date = db.Column(db.Date, nullable=False)
    has_reference_seq_zip: bool = db.Column(db.Boolean, nullable=False)
    has_results_zip: bool = db.Column(db.Boolean, nullable=False)

    def results_dir(self) -> str:
        return f"{_get_basepath(self.date)}/results"

    def results_file_path(self) -> str:
        return f"{self.results_dir()}/{self.primary_key}_{self.name}.zip"

    def reference_seq_zip_path(self) -> str:
        return f"{_get_basepath(self.date)}/inputs/references/{self.primary_key}_{self.name}.zip"


def _samples_this_week(current_date: datetime.date):
    start_of_week = get_start_of_week(current_date)
    return (
        db.session.execute(
            db.select(Sample)
            .filter(Sample.date >= start_of_week)
            .filter(Sample.date < start_of_week + datetime.timedelta(weeks=1))
        )
        .scalars()
        .all()
    )


def _count_samples_this_week(current_date: datetime.date) -> int:
    return len(_samples_this_week(current_date))


def remaining_samples_this_week(
    current_date: Optional[datetime.date] = None,
) -> Dict:
    if current_date is None:
        current_date = datetime.date.today()
    settings = get_current_settings()
    year, week, day = current_date.isocalendar()
    message = ""
    max_samples = settings["plate_n_rows"] * settings["plate_n_cols"]
    remaining = max_samples - _count_samples_this_week(current_date)
    if day > settings["last_submission_day"]:
        remaining = 0
        message = "Sample submission is closed for this week."
    elif remaining == 0:
        message = "All samples have been taken this week."
    return {"remaining": remaining, "message": message}


def _get_basepath(current_date: datetime.date) -> str:
    year, week, _ = current_date.isocalendar()
    data_path = flask.current_app.config["CIRCUITSEQ_DATA_PATH"]
    return f"{data_path}/{year}/{week}"


def _write_samples_as_tsv_this_week(current_date: datetime.date) -> None:
    filename = f"{_get_basepath(current_date)}/inputs/samples.tsv"
    logger.info(f"Generating {filename}")
    with open(filename, "w", newline="") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t", lineterminator="\n")
        columns = [
            "date",
            "primary_key",
            "tube_primary_key",
            "email",
            "name",
            "running_option",
            "concentration",
        ]
        writer.writerow(columns)
        for sample in _samples_this_week(current_date):
            logger.info(f"  - {sample.primary_key}")
            writer.writerow([getattr(sample, column) for column in columns])


def update_samples_zipfile(current_date: Optional[datetime.date] = None) -> str:
    if current_date is None:
        current_date = datetime.date.today()
    base_path = _get_basepath(current_date)
    inputs_dir = f"{base_path}/inputs"
    pathlib.Path(inputs_dir).mkdir(parents=True, exist_ok=True)
    _write_samples_as_tsv_this_week(current_date)
    logger.info(f"Creating zip file of {inputs_dir}..")
    zip_filename = shutil.make_archive(
        base_name=f"{base_path}/samples",
        format="zip",
        root_dir=f"{base_path}/inputs",
    )
    logger.info(f"  -> created zip file {zip_filename}")
    return zip_filename


def get_samples(email: Optional[str] = None) -> Dict[str, List[Sample]]:
    samples = {}
    start_of_week = get_start_of_week()
    selected_samples = db.select(Sample).order_by(db.desc("date"))
    if email is not None:
        selected_samples = selected_samples.filter(Sample.email == email)
    samples["current_samples"] = (
        db.session.execute(selected_samples.filter(Sample.date >= start_of_week))
        .scalars()
        .all()
    )
    samples["previous_samples"] = (
        db.session.execute(selected_samples.filter(Sample.date < start_of_week))
        .scalars()
        .all()
    )
    return samples


def _new_email_message(email: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = "no-reply@predictcr.iwr.uni-heidelberg.de"
    msg["To"] = email
    return msg


def _wrap_email_message(email: str, message: str) -> str:
    return f"Dear {email},\n\n{message}\n\nBest wishes,\n\npredicTCR Team.\nhttps://predictcr.iwr.uni-heidelberg.de"


def _send_email_message(email_message: EmailMessage) -> None:
    postfix_server_address = "email:587"
    with smtplib.SMTP(postfix_server_address) as s:
        s.send_message(email_message)


def _send_result_email(
    sample: Sample, success: bool, result_files: Optional[List[pathlib.Path]] = None
) -> Tuple[str, int]:
    message_head = f"Your sample {sample.primary_key}_{sample.name} has been processed"
    if success:
        message_body = (
            ", and you can download the full analysis data by "
            "logging in to your account at https://predictcr.iwr.uni-heidelberg.de"
        )
    else:
        message_body = (
            ", however no correct de-novo assembly has been determined.\n\n"
            "Please consider handing in this sample next week again."
        )
    try:
        logger.info(
            f"Sending {sample.primary_key} success={success} result email to {sample.email}"
        )
        msg = _new_email_message(sample.email)
        msg.set_content(
            _wrap_email_message(sample.email, f"{message_head}{message_body}")
        )
        msg["Subject"] = (
            f"predicTCR results for sample {sample.primary_key}_{sample.name}"
        )
        if success is True:
            for result_file in result_files:
                with open(result_file, "rb") as fp:
                    result_file_data = fp.read()
                msg.add_attachment(
                    result_file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=result_file.name,
                )
        _send_email_message(msg)
    except Exception as e:
        logger.warning(f"  --> failed to send result email: {e}")
        return (
            f"Failed to send results email for {sample.primary_key} to {sample.email}: {e}",
            400,
        )
    return (
        f"Results email for {sample.primary_key} sent to {sample.email}",
        200,
    )


def _is_valid_filename(primary_key: str, filename: str) -> bool:
    segments = pathlib.Path(filename).name.split("_")
    if len(segments) < 3:
        return False
    yy = segments[0]
    ww = segments[1]
    nn = segments[2]
    return primary_key == f"{yy}_{ww}_{nn}"


def process_result(
    primary_key: str, success: bool, result_zip_file: Optional[FileStorage]
) -> Tuple[str, int]:
    sample = db.session.execute(
        db.select(Sample).filter_by(primary_key=primary_key)
    ).scalar_one_or_none()
    if sample is None:
        logger.warning(f" --> Unknown primary key {primary_key}")
        return f"Unknown primary key {primary_key}", 400
    if sample.tube_primary_key != sample.primary_key:
        logger.info(
            f"Tube key '{sample.tube_primary_key}' differs from primary key '{primary_key}' -> using tube key"
        )
        return process_result(sample.tube_primary_key, success, result_zip_file)
    if success is False:
        logger.info("Sending result failure message for {primary_key}")
        sample.has_results_zip = False
        db.session.commit()
        return _send_result_email(sample, success)
    if result_zip_file is None:
        logger.warning(" --> No zipfile")
        return "Zip file missing", 400
    logger.info(
        f"Processing zip file {result_zip_file} for {primary_key} --> {sample.results_file_path()}"
    )
    pathlib.Path(sample.results_dir()).mkdir(parents=True, exist_ok=True)
    result_zip_file.save(sample.results_file_path())
    sample.has_results_zip = True
    db.session.commit()
    result_files = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            zip_file = zipfile.ZipFile(sample.results_file_path())
            zip_file.extract("email.txt", tmp_dir)
            with open(f"{tmp_dir}/email.txt") as f:
                files_to_email = f.readlines()
            for file_to_email in files_to_email:
                file_to_email = file_to_email.strip()
                logger.info(f"Trying to extract {file_to_email} from zipfile")
                try:
                    result_files.append(
                        pathlib.Path(zip_file.extract(file_to_email, tmp_dir))
                    )
                    logger.info(f"--> extracted {file_to_email}")
                except Exception as e:
                    logging.warning(f"Failed to extract file {file_to_email}: {e}")
        except Exception as e:
            logger.warning(f"Failed to process zip file: {e}")
        email_message, _ = _send_result_email(sample, success, result_files)
    return f"Results file saved, {email_message}", 200


@dataclass
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    activated = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

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
            "is_admin": self.is_admin,
        }


def is_valid_email(email: str) -> bool:
    return re.match(r"\S+@((\S*heidelberg)|embl|dkfz)\.de$", email) is not None


def is_valid_password(password: str) -> bool:
    return re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$", password) is not None


def _send_activation_email(email: str):
    secret_key = flask.current_app.config["JWT_SECRET_KEY"]
    token = encode_activation_token(email, secret_key)
    url = f"https://predictcr.iwr.uni-heidelberg.de/activate/{token}"
    logger.info(f"Activation url: {url}")
    msg = _new_email_message(email)
    msg_body = (
        f"To activate your predicTCR account,"
        f"please confirm your email address by clicking on the following link:\n\n"
        f"{url}\n\n"
        f"If you did not sign up for an account please disregard this email."
    )
    msg.set_content(_wrap_email_message(email, msg_body))
    msg["Subject"] = "predicTCR account activation"
    _send_email_message(msg)


def send_password_reset_email(email: str) -> Tuple[str, int]:
    user = db.session.execute(
        db.select(User).filter(User.email == email)
    ).scalar_one_or_none()
    msg = _new_email_message(email)
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
        url = f"https://predictcr.iwr.uni-heidelberg.de/reset_password/{token}"
        logger.info(f"Password reset url: {url}")
        msg_body = (
            f"To reset the password for your predicTCR account, "
            f"please click on the following link (valid for 1 hour):\n\n"
            f"{url}\n\n"
            f"If you did not make this password reset request please disregard this email."
        )
    msg.set_content(_wrap_email_message(email, msg_body))
    msg["Subject"] = "predicTCR password reset"
    _send_email_message(msg)
    return f"Sent password reset email to '{email}'", 200


def add_new_user(email: str, password: str, is_admin: bool) -> Tuple[str, int]:
    if not is_valid_email(email):
        return "Please use a uni-heidelberg, dkfz or embl email address.", 400
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
                is_admin=is_admin,
            )
        )
        db.session.commit()
    except Exception as e:
        logger.warning(f"Error adding user to db: {e}")
        return "Failed to create new user", 400
    return (
        f"Successful signup for {email}. To activate your account, please click on the link in the activation email from no-reply@predictcr.iwr.uni-heidelberg.de sent to this email address",
        200,
    )


def activate_user(token: str) -> Tuple[str, int]:
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


def reset_user_password(token: str, email: str, new_password: str) -> Tuple[str, int]:
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


def _get_new_key(today: datetime) -> Tuple[Optional[str], str]:
    year, week, day = today.isocalendar()
    count = _count_samples_this_week(today)
    settings = get_current_settings()
    remaining_samples = remaining_samples_this_week()
    if remaining_samples["remaining"] == 0:
        return None, remaining_samples["message"]
    key = get_primary_key(
        year=year,
        week=week,
        current_count=count,
        n_rows=settings["plate_n_rows"],
        n_cols=settings["plate_n_cols"],
    )
    return key, ""


def add_new_sample(
    email: str,
    name: str,
    running_option: str,
    concentration: int,
    reference_sequence_files: List[FileStorage],
) -> Tuple[Optional[Sample], str]:
    today = datetime.date.today()
    base_path = _get_basepath(today)
    key, message = _get_new_key(today)
    if key is None:
        return None, message
    has_reference_seq_zip = False
    ref_seq_dir = pathlib.Path(f"{base_path}/inputs/references")
    ref_seq_dir.mkdir(parents=True, exist_ok=True)
    if len(reference_sequence_files) > 0:
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                for reference_sequence_file in reference_sequence_files:
                    filename = secure_filename(reference_sequence_file.filename)
                    temp_file = pathlib.Path(tmp_dir) / filename
                    logger.info(
                        f"Saving {reference_sequence_file.filename} to temporary file {temp_file}"
                    )
                    reference_sequence_file.save(temp_file)
                ref_seq_basename = str(ref_seq_dir / f"{key}_{name}")
                zip_filename = shutil.make_archive(
                    base_name=ref_seq_basename,
                    format="zip",
                    root_dir=tmp_dir,
                )
                logger.info(f"  -> created zip file {zip_filename}")
            has_reference_seq_zip = True
        except Exception as e:
            logger.warning("Failed to process supplied reference sequence files")
            # todo: should we return an error here instead of continuing without the files?
            logger.exception(e)
    new_sample = Sample(
        email=email,
        primary_key=key,
        tube_primary_key=key,
        name=name,
        running_option=running_option,
        concentration=concentration,
        has_reference_seq_zip=has_reference_seq_zip,
        date=today,
        has_results_zip=False,
    )
    db.session.add(new_sample)
    db.session.commit()
    return new_sample, ""


def resubmit_sample(primary_key: str) -> Tuple[str, int]:
    sample = db.session.execute(
        db.select(Sample).filter_by(primary_key=primary_key)
    ).scalar_one_or_none()
    if sample is None:
        logger.warning(f" --> Unknown primary_key '{primary_key}'")
        return f"Unknown Primary Key '{primary_key}'", 400
    today = datetime.date.today()
    new_primary_key, message = _get_new_key(today)
    if new_primary_key is None:
        return message, 400
    new_sample = Sample(
        email="RESUBMITTED",
        primary_key=new_primary_key,
        tube_primary_key=sample.tube_primary_key,
        name=sample.name,
        running_option=sample.running_option,
        concentration=sample.concentration,
        date=today,
        has_reference_seq_zip=sample.has_reference_seq_zip,
        has_results_zip=False,
    )
    if sample.has_reference_seq_zip:
        pathlib.Path(new_sample.reference_seq_zip_path()).resolve().parent.mkdir(
            parents=True, exist_ok=True
        )
        shutil.copy(
            sample.reference_seq_zip_path(), new_sample.reference_seq_zip_path()
        )
    db.session.add(new_sample)
    db.session.commit()
    return (
        f"Resubmitted sample '{primary_key}' with new primary key '{new_primary_key}'",
        200,
    )
