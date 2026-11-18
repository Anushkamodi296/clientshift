import pytest
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.api.routes.auth import (
    signup,
    login,
    google_auth,
    guest_mode,
    get_me,
    hash_password,
    create_jwt_token,
    decode_jwt_token
)
from app.db.models import SignupRequest, LoginRequest, GoogleAuthRequest
from app.db.repository import Repository
from fastapi import HTTPException

def test_hash_password_and_jwt():
    pwd = "secret_password_123"
    h1 = hash_password(pwd)
    h2 = hash_password(pwd)
    assert h1 == h2
    assert h1 != hash_password("other_pwd")

    token = create_jwt_token("usr_test_1", "test@clientshift.dev")
    decoded = decode_jwt_token(token)
    assert decoded["sub"] == "usr_test_1"
    assert decoded["email"] == "test@clientshift.dev"

import uuid

def test_signup_and_duplicate():
    unique_email = f"architect_{uuid.uuid4().hex[:8]}@clientshift.io"
    req = SignupRequest(
        email=unique_email,
        password="secure_password_99",
        full_name="Elena Rostova"
    )
    res = signup(req)
    assert res.user.email == unique_email
    assert res.user.full_name == "Elena Rostova"
    assert len(res.access_token) > 20

    # Duplicate should raise 400
    with pytest.raises(HTTPException) as excinfo:
        signup(req)
    assert excinfo.value.status_code == 400

def test_login_success_and_failure():
    unique_email = f"login_{uuid.uuid4().hex[:8]}@clientshift.io"
    signup(SignupRequest(
        email=unique_email,
        password="secure_password_99",
        full_name="Login Test User"
    ))
    # Login existing
    login_req = LoginRequest(
        email=unique_email,
        password="secure_password_99"
    )
    res = login(login_req)
    assert res.user.email == unique_email
    assert len(res.access_token) > 20

    # Bad password
    bad_req = LoginRequest(
        email=unique_email,
        password="wrong_password"
    )
    with pytest.raises(HTTPException) as excinfo:
        login(bad_req)
    assert excinfo.value.status_code == 401

def test_google_auth_and_guest_mode():
    g_req = GoogleAuthRequest(
        email="google.lead@gmail.com",
        full_name="Lead Googler",
        avatar_url="https://example.com/avatar.png"
    )
    g_res = google_auth(g_req)
    assert g_res.user.email == "google.lead@gmail.com"
    assert g_res.user.provider == "google"

    guest_res = guest_mode()
    assert guest_res.user.provider == "guest"
    assert "guest" in guest_res.user.email

def test_get_me_with_bearer_token():
    guest_res = guest_mode()
    auth_header = f"Bearer {guest_res.access_token}"
    me = get_me(authorization=auth_header)
    assert me["user"].email == guest_res.user.email
    assert "saved_migrations" in me["stats"].model_dump()
    assert "benchmark_runs" in me["stats"].model_dump()
