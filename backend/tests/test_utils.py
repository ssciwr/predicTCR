from __future__ import annotations
from predicTCR_server.utils import (
    encode_password_reset_token,
    decode_password_reset_token,
)
from predicTCR_server.utils import encode_activation_token, decode_activation_token


def test_password_reset_token():
    email = "asdfads@dasfgdasf.com"
    secret = "p23c5fn78nd"
    token = encode_password_reset_token(email, secret)
    decoded_email = decode_password_reset_token(token, secret)
    assert decoded_email == email
    decoded_email = decode_password_reset_token(token, "wrong secret")
    assert decoded_email is None
    decoded_email = decode_password_reset_token("invalid-token", secret)
    assert decoded_email is None


def test_activation_token():
    email = "asdfads@dasfgdasf.com"
    secret = "p23c5fn78nd"
    token = encode_activation_token(email, secret)
    decoded_email = decode_activation_token(token, secret)
    assert decoded_email == email
    decoded_email = decode_activation_token(token, "wrong secret")
    assert decoded_email is None
    decoded_email = decode_activation_token("invalid-token", secret)
    assert decoded_email is None
