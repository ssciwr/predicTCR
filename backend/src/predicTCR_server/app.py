from __future__ import annotations

import os
import secrets
import datetime
import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import cross_origin
from predicTCR_server.logger import get_logger
from predicTCR_server.model import (
    db,
    Sample,
    User,
    add_new_user,
    add_new_runner_user,
    reset_user_password,
    enable_user,
    activate_user,
    add_new_sample,
    get_samples,
    send_password_reset_email,
    request_job,
    process_result,
)


def create_app(data_path: str = "/predictcr_data"):
    logger = get_logger()
    app = Flask("predicTCRServer")
    jwt_secret_key = os.environ.get("JWT_SECRET_KEY")
    if jwt_secret_key is not None and len(jwt_secret_key) > 16:
        logger.info("Setting JWT_SECRET_KEY from supplied env var")
        app.config["JWT_SECRET_KEY"] = jwt_secret_key
    else:
        logger.warning(
            "JWT_SECRET_KEY env var not set or too short: generating random secret key"
        )
        # new secret key -> invalidates any existing tokens
        app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(64)
    # tokens are by default valid for 1 hour
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=60)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data_path}/predicTCR.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # limit max file upload size to 100mb
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
    app.config["PREDICTCR_DATA_PATH"] = data_path

    jwt = JWTManager(app)
    db.init_app(app)

    # https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_identity_loader
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_lookup_loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.execute(
            db.select(User).filter(User.id == identity)
        ).scalar_one_or_none()

    @app.route("/api/login", methods=["POST"])
    def login():
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        logger.info(f"Login request from {email}")
        user = db.session.execute(
            db.select(User).filter(User.email == email)
        ).scalar_one_or_none()
        if not user:
            logger.info("  -> user not found")
            return jsonify(message="Unknown email address"), 400
        if not user.activated:
            logger.info("  -> user not activated")
            return jsonify(message="User account is not yet activated"), 400
        if not user.enabled:
            logger.info("  -> user not enabled")
            return jsonify(message="User account is not yet enabled"), 400
        if not user.check_password(password):
            logger.info("  -> wrong password")
            return jsonify(message="Incorrect password"), 400
        logger.info("  -> returning JWT access token")
        access_token = create_access_token(identity=user)
        return jsonify(user=user.as_dict(), access_token=access_token)

    @app.route("/api/signup", methods=["POST"])
    def signup():
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        logger.info(f"Signup request from {email}")
        message, code = add_new_user(email, password, False)
        return jsonify(message=message), code

    @app.route("/api/activate/<token>")
    def activate(token: str):
        message, code = activate_user(token)
        return jsonify(message=message), code

    @app.route("/api/request_password_reset", methods=["POST"])
    def request_password_reset():
        message, code = send_password_reset_email(request.json.get("email", ""))
        return jsonify(message=message), code

    @app.route("/api/reset_password", methods=["POST"])
    def reset_password():
        token = request.json.get("reset_token", None)
        if token is None:
            return jsonify(message="Reset token missing"), 400
        email = request.json.get("email", None)
        if email is None:
            return jsonify(message="Email address missing"), 400
        new_password = request.json.get("new_password", None)
        if new_password is None:
            return jsonify(message="New password missing"), 400
        message, code = reset_user_password(token, email, new_password)
        return jsonify(message=message), code

    @app.route("/api/change_password", methods=["POST"])
    @jwt_required()
    def change_password():
        current_password = request.json.get("current_password", None)
        if current_password is None:
            return jsonify(message="Current password missing"), 400
        new_password = request.json.get("new_password", None)
        if new_password is None:
            return jsonify(message="New password missing"), 400
        logger.info(f"Password change request from {current_user.email}")
        if current_user.set_password(current_password, new_password):
            return jsonify(message="Password changed.")
        return (
            jsonify(message="Failed to change password: current password incorrect."),
            400,
        )

    @app.route("/api/samples", methods=["GET"])
    @jwt_required()
    def samples():
        return get_samples(current_user.email)

    @app.route("/api/input_h5_file", methods=["POST"])
    @jwt_required()
    def input_h5_file():
        sample_id = request.json.get("sample_id", None)
        logger.info(
            f"User {current_user.email} requesting results for sample {sample_id}"
        )
        filters = {"id": sample_id}
        if not current_user.is_admin and not current_user.is_runner:
            filters["email"] = current_user.email
        user_sample = db.session.execute(
            db.select(Sample).filter_by(**filters)
        ).scalar_one_or_none()
        if user_sample is None:
            logger.info(f"  -> sample {sample_id} not found")
            return jsonify(message="Sample not found"), 400
        return flask.send_file(user_sample.input_h5_file_path(), as_attachment=True)

    @app.route("/api/input_csv_file", methods=["POST"])
    @jwt_required()
    def input_csv_file():
        sample_id = request.json.get("sample_id", None)
        logger.info(
            f"User {current_user.email} requesting results for sample {sample_id}"
        )
        filters = {"id": sample_id}
        if not current_user.is_admin and not current_user.is_runner:
            filters["email"] = current_user.email
        user_sample = db.session.execute(
            db.select(Sample).filter_by(**filters)
        ).scalar_one_or_none()
        if user_sample is None:
            logger.info(f"  -> sample {sample_id} not found")
            return jsonify(message="Sample not found"), 400
        return flask.send_file(user_sample.input_csv_file_path(), as_attachment=True)

    @app.route("/api/result", methods=["POST"])
    @jwt_required()
    def result():
        sample_id = request.json.get("sample_id", None)
        logger.info(
            f"User {current_user.email} requesting results for sample {sample_id}"
        )
        filters = {"id": sample_id}
        if not current_user.is_admin:
            filters["email"] = current_user.email
        user_sample = db.session.execute(
            db.select(Sample).filter_by(**filters)
        ).scalar_one_or_none()
        if user_sample is None:
            logger.info(f"  -> sample {sample_id} not found")
            return jsonify(message="Sample not found"), 400
        if not user_sample.has_results_zip:
            logger.info(f"  -> sample {sample_id} found but no results available")
            return jsonify(message="No results available"), 400
        requested_file = user_sample.result_file_path()
        if not requested_file.is_file():
            logger.info(f"  -> file {requested_file} not found")
            return jsonify(message="Results file not found"), 400
        logger.info(f"Returning file {requested_file}")
        return flask.send_file(requested_file, as_attachment=True)

    @app.route("/api/sample", methods=["POST"])
    @jwt_required()
    def add_sample():
        email = current_user.email
        form_as_dict = request.form.to_dict()
        name = form_as_dict.get("name", "")
        tumor_type = form_as_dict.get("tumor_type", "")
        source = form_as_dict.get("source", "")
        h5_file = request.files.get("h5_file")
        csv_file = request.files.get("csv_file")
        logger.info(f"Adding sample {name} from {email}")
        new_sample, error_message = add_new_sample(
            email, name, tumor_type, source, h5_file, csv_file
        )
        if new_sample is not None:
            logger.info("  - > success")
            return jsonify(sample=new_sample)
        return jsonify(message=error_message), 400

    @app.route("/api/admin/samples", methods=["GET"])
    @jwt_required()
    def admin_all_samples():
        if not current_user.is_admin:
            return jsonify(message="Admin account required"), 400
        return jsonify(get_samples())

    @app.route("/api/admin/enable_user", methods=["POST"])
    @jwt_required()
    def admin_enable_user():
        if not current_user.is_admin:
            return jsonify(message="Admin account required"), 400
        user_email = request.json.get("user_email", "")
        message, code = enable_user(user_email, True)
        return jsonify(message=message), code

    @app.route("/api/admin/disable_user", methods=["POST"])
    @jwt_required()
    def admin_disable_user():
        if not current_user.is_admin:
            return jsonify(message="Admin account required"), 400
        user_email = request.json.get("user_email", "")
        message, code = enable_user(user_email, False)
        return jsonify(message=message), code

    @app.route("/api/admin/users", methods=["GET"])
    @jwt_required()
    def admin_users():
        if not current_user.is_admin:
            return jsonify(message="Admin account required"), 400
        users = (
            db.session.execute(db.select(User).order_by(db.desc(User.id)))
            .scalars()
            .all()
        )
        return jsonify(users=[user.as_dict() for user in users])

    @app.route("/api/admin/runner_token", methods=["GET"])
    @jwt_required()
    def admin_runner_token():
        if not current_user.is_admin:
            return jsonify(message="Admin account required"), 400
        runner_user = add_new_runner_user()
        if runner_user is None:
            return jsonify(message="Failed to create runner account"), 500
        access_token = create_access_token(
            identity=runner_user, expires_delta=datetime.timedelta(weeks=26)
        )
        return jsonify(access_token=access_token)

    @app.route("/api/runner/request_job", methods=["POST"])
    @cross_origin()
    @jwt_required()
    def runner_request_job():
        if not current_user.is_runner:
            return jsonify(message="Runner account required"), 400
        runner_hostname = request.json.get("runner_hostname", "")
        logger.info(f"Runner {current_user.email} / {runner_hostname} requesting job")
        sample_id = request_job()
        if sample_id is None:
            return jsonify(message="No job available"), 204
        return {"sample_id": sample_id}

    @app.route("/api/runner/result", methods=["POST"])
    @cross_origin()
    @jwt_required()
    def runner_result():
        if not current_user.is_runner:
            return jsonify(message="Runner account required"), 400
        form_as_dict = request.form.to_dict()
        sample_id = form_as_dict.get("sample_id", None)
        if sample_id is None:
            return jsonify(message="Missing key: sample_id"), 400
        success = form_as_dict.get("success", None)
        if success is None or success.lower() not in ["true", "false"]:
            logger.info("  -> missing success key")
            return jsonify(message="Missing key: success=True/False"), 400
        success = success.lower() == "true"
        zipfile = request.files.to_dict().get("file", None)
        if success is True and zipfile is None:
            logger.info("  -> missing zipfile")
            return jsonify(message="Result has success=True but no file"), 400
        runner_hostname = form_as_dict.get("runner_hostname", "")
        logger.info(
            f"Result upload for '{sample_id}' from runner {current_user.email} / {runner_hostname}"
        )
        error_message = form_as_dict.get("error_message", None)
        if error_message is not None:
            logger.info(f"  -> error message: {error_message}")
        message, code = process_result(sample_id, success, zipfile)
        return jsonify(message=message), code

    with app.app_context():
        db.create_all()

    return app
