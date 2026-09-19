import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("s3cret-password")
    assert hashed != "s3cret-password"
    assert verify_password("s3cret-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_hash_is_salted():
    assert hash_password("same") != hash_password("same")


def test_token_roundtrip():
    token = create_access_token(42)
    assert decode_access_token(token) == 42


def test_invalid_token_returns_none():
    assert decode_access_token("not-a-jwt") is None


def test_tampered_token_returns_none():
    token = create_access_token(42)
    assert decode_access_token(token + "x") is None


def test_expired_token_returns_none(monkeypatch):
    from app.core import security

    monkeypatch.setattr(security.get_settings(), "jwt_expire_minutes", -1)
    token = security.create_access_token(42)
    assert decode_access_token(token) is None
