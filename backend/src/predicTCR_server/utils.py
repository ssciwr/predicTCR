from __future__ import annotations
from typing import Optional
import datetime
from predicTCR_server.logger import get_logger
import string
import math
from itsdangerous.url_safe import URLSafeTimedSerializer

logger = get_logger("predicTCRServer")


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


def get_start_of_week(current_date: Optional[datetime.date] = None) -> datetime.date:
    if current_date is None:
        current_date = datetime.date.today()
    year, week, day = current_date.isocalendar()
    return datetime.date.fromisocalendar(year, week, 1)


def get_primary_key(
    year: int, week: int, current_count: int, n_rows: int, n_cols: int
) -> Optional[str]:
    max_samples = n_rows * n_cols
    row_labels = string.ascii_uppercase
    if current_count >= max_samples:
        return None

    i_row = math.floor(current_count / n_cols)
    i_col = current_count % n_cols
    yy = year % 100
    return f"{yy:02d}_{week:02d}_{row_labels[i_row]}{i_col + 1}"
