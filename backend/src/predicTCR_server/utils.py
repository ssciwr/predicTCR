from __future__ import annotations
from typing import Optional
from predicTCR_server.logger import get_logger
from itsdangerous.url_safe import URLSafeTimedSerializer
from datetime import datetime

logger = get_logger()


def timestamp_now() -> int:
    return int(datetime.now().timestamp())


def _encode_string_as_token(string_to_encode: str, salt: str, secret_key: str) -> str:
    ss = URLSafeTimedSerializer(secret_key, salt=salt)
    return ss.dumps(string_to_encode)


def _decode_string_from_token(
    token: str, salt: str, secret_key: str, max_age_secs: int
) -> Optional[str]:
    ss = URLSafeTimedSerializer(secret_key, salt=salt)
    try:
        email = ss.loads(token, max_age=max_age_secs)
    except Exception as e:
        logger.warning(f"Invalid or expired {salt} token: {e}")
        return None
    return email


def encode_activation_token(email: str, secret_key: str) -> str:
    return _encode_string_as_token(email, "activate", secret_key)


def decode_activation_token(token: str, secret_key: str) -> Optional[str]:
    one_week_in_secs = 60 * 60 * 24 * 7
    return _decode_string_from_token(token, "activate", secret_key, one_week_in_secs)


def encode_password_reset_token(email: str, secret_key: str) -> str:
    return _encode_string_as_token(email, "password-reset", secret_key)


def decode_password_reset_token(token: str, secret_key: str) -> Optional[str]:
    one_hour_in_secs = 60 * 60
    return _decode_string_from_token(
        token, "password-reset", secret_key, one_hour_in_secs
    )
