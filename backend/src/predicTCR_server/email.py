from __future__ import annotations

import smtplib
from email.message import EmailMessage
from predicTCR_server.settings import predicTCR_url


def _wrap_email_message(email: str, message: str) -> str:
    return f"Dear {email},\n\n{message}\n\nBest wishes,\n\npredicTCR Team.\nhttps://{predicTCR_url}"


def _send_email_message(email_message: EmailMessage) -> None:
    postfix_server_address = "email:587"
    with smtplib.SMTP(postfix_server_address) as s:
        s.send_message(email_message)


def send_email(email: str, subject: str, message: str) -> None:
    msg = EmailMessage()
    msg["From"] = f"no-reply@{predicTCR_url}"
    msg["To"] = email
    msg.set_content(_wrap_email_message(email, message))
    msg["Subject"] = subject
    _send_email_message(msg)
