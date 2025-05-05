from __future__ import annotations
import predicTCR_server.model as model
from predicTCR_server.settings import predicTCR_url
import secrets


def _count_users() -> int:
    return len(model.db.session.execute(model.db.select(model.User)).scalars().all())


def test_add_new_user_invalid(app):
    password_valid = "abcABC123"
    email_valid = "joe.bloggs@embl.de"
    with app.app_context():
        for email in ["joe@gmail", "@embl.de"]:
            msg, code = model.add_new_user(email, password_valid, is_admin=False)
            assert code == 400
            assert "email" in msg
        for password in [
            "",
            "abc123A",
            "passwordpassword",
            "abc12345678",
            "asd!(*&@#@!(*#%ASDASDFGK",
        ]:
            msg, code = model.add_new_user(email_valid, password, is_admin=False)
            assert code == 400
            assert "Password" in msg
        msg, code = model.add_new_user("user@abc.xy", password_valid, is_admin=False)
        assert code == 400
        assert msg == "This email address is already in use"


def test_add_new_user_valid(app):
    email = "x@embl.de"
    password = "passwdP1"
    with app.app_context():
        n_users = _count_users()
        msg, code = model.add_new_user(email, password, is_admin=False)
        assert code == 200
        assert _count_users() == n_users + 1
        user = model.db.session.execute(
            model.db.select(model.User).filter(model.User.email == email)
        ).scalar_one_or_none()
        assert user is not None
        assert user.email == email
        assert user.is_admin is False
        assert user.activated is False
        email_msg = app.config["TESTING_ONLY_LAST_SMTP_MESSAGE"]
        assert email_msg["To"] == email
        # extract activation token from email contents
        body = str(email_msg.get_body()).replace("=\n", "")
        activation_token = body.split(f"https://{predicTCR_url}/activate/")[1].split(
            "\n"
        )[0]
        # check password pre-activation
        assert user.check_password("wrong") is False
        assert user.check_password(password) is True
        # activate account with invalid token
        model.activate_user("not_a_real_activation_token")
        assert user.activated is False
        # activate account with valid token
        model.activate_user(activation_token)
        assert user.activated is True
        # enable user
        model.update_user({"email": email, "enabled": True})
        # user gets an email when their account has been enabled
        email_msg = app.config["TESTING_ONLY_LAST_SMTP_MESSAGE"]
        assert email_msg["To"] == email
        body = str(email_msg.get_body()).replace("=\n", "")
        assert "account has been enabled" in body.lower()
        # set new password
        assert user.set_password("wrong", "new") is False
        assert user.check_password(password) is True
        assert user.set_password(password, "newPassword2") is True
        assert user.activated is True
        # check new password
        assert user.check_password(password) is False
        assert user.check_password("newPassword2") is True
        assert user.activated is True


def test_send_password_reset_email_invalid(app):
    with app.app_context():
        email = "invalid@embl.de"
        model.send_password_reset_email(email)
        last_email_msg = app.config.get("TESTING_ONLY_LAST_SMTP_MESSAGE")
        assert last_email_msg is not None
        assert last_email_msg["To"] == email
        body = str(last_email_msg.get_body()).replace("=\n", "")
        # no reset url in email
        assert f"https://{predicTCR_url}/reset_password/" not in body
        assert "no predictcr account was found for this address" in body.lower()


def test_reset_password(app):
    with app.app_context():
        email = "user@abc.xy"
        new_password = secrets.token_urlsafe()
        model.send_password_reset_email(email)
        last_email_msg = app.config.get("TESTING_ONLY_LAST_SMTP_MESSAGE")
        assert last_email_msg is not None
        assert last_email_msg["To"] == email
        body = str(last_email_msg.get_body()).replace("=\n", "")
        # extract reset token from email contents
        reset_token = body.split(f"https://{predicTCR_url}/reset_password/")[1].split(
            "\n"
        )[0]
        # use incorrect token
        msg, code = model.reset_user_password("wrongtoken", email, new_password)
        assert "invalid" in msg.lower()
        assert code == 400
        # use incorrect email
        msg, code = model.reset_user_password(
            reset_token, "wrong@email.com", new_password
        )
        assert "invalid" in msg.lower()
        assert code == 400
        # use correct token & email
        msg, code = model.reset_user_password(reset_token, email, new_password)
        assert "password changed" in msg.lower()
        assert code == 200
        user = model.db.session.execute(
            model.db.select(model.User).filter(model.User.email == email)
        ).scalar_one_or_none()
        assert user is not None
        assert user.email == email
        assert user.check_password(new_password) is True
