import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import APIRouter, HTTPException, Header, Depends
from app.db.models import (
    LoginRequest,
    SignupRequest,
    GoogleAuthRequest,
    AuthTokenResponse,
    UserProfile,
    UserStats
)
from app.db.repository import Repository

router = APIRouter()
repository = Repository()

JWT_SECRET = "clientshift_hyper_futuristic_jwt_secret_token_key_2026"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 72

def hash_password(password: str) -> str:
    # Deterministic salted SHA-256
    salt = "clientshift_salt_seed_v1"
    return hashlib.sha256(f"{salt}_{password}".encode("utf-8")).hexdigest()

def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired, please sign in again")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization token")

@router.post("/signup", response_model=AuthTokenResponse)
def signup(req: SignupRequest):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="A valid email address is required")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if not req.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")

    existing = repository.get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    pwd_hash = hash_password(req.password)
    now = datetime.now(timezone.utc).isoformat()
    avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}&backgroundColor=00f2fe,8a2be2"

    user = repository.create_user(
        user_id=user_id,
        email=email,
        full_name=req.full_name.strip(),
        password_hash=pwd_hash,
        provider="local",
        avatar_url=avatar,
        created_at=now
    )
    token = create_jwt_token(user.id, user.email)
    stats = repository.get_user_stats(user.id)

    return AuthTokenResponse(
        access_token=token,
        user=user,
        stats=stats
    )

@router.post("/login", response_model=AuthTokenResponse)
def login(req: LoginRequest):
    email = req.email.strip().lower()
    existing = repository.get_user_by_email(email)
    if not existing:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    pwd_hash = hash_password(req.password)
    if existing.get("password_hash") != pwd_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = UserProfile(
        id=existing["id"],
        email=existing["email"],
        full_name=existing["full_name"],
        avatar_url=existing.get("avatar_url"),
        provider=existing.get("provider", "local"),
        created_at=existing["created_at"]
    )
    token = create_jwt_token(user.id, user.email)
    stats = repository.get_user_stats(user.id)

    return AuthTokenResponse(
        access_token=token,
        user=user,
        stats=stats
    )

@router.post("/google", response_model=AuthTokenResponse)
def google_auth(req: GoogleAuthRequest):
    # Extracts profile from Google token or client payload
    email = (req.email or "engineer.alex@clientshift.dev").strip().lower()
    full_name = req.full_name or "Alex Vance (Google Lead)"
    avatar = req.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}&backgroundColor=00f2fe"

    # Decode Google JWT credential if supplied
    if req.credential:
        try:
            unverified = jwt.decode(req.credential, options={"verify_signature": False})
            email = unverified.get("email", email).strip().lower()
            full_name = unverified.get("name", full_name)
            avatar = unverified.get("picture", avatar)
        except Exception:
            pass

    existing = repository.get_user_by_email(email)
    now = datetime.now(timezone.utc).isoformat()
    if existing:
        user_id = existing["id"]
        user = repository.create_user(
            user_id=user_id,
            email=email,
            full_name=full_name,
            password_hash=None,
            provider="google",
            avatar_url=avatar,
            created_at=existing["created_at"]
        )
    else:
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        user = repository.create_user(
            user_id=user_id,
            email=email,
            full_name=full_name,
            password_hash=None,
            provider="google",
            avatar_url=avatar,
            created_at=now
        )

    token = create_jwt_token(user.id, user.email)
    stats = repository.get_user_stats(user.id)

    return AuthTokenResponse(
        access_token=token,
        user=user,
        stats=stats
    )

@router.post("/guest", response_model=AuthTokenResponse)
def guest_mode():
    guest_email = "guest.engineer@clientshift.io"
    existing = repository.get_user_by_email(guest_email)
    now = datetime.now(timezone.utc).isoformat()
    if existing:
        user = UserProfile(
            id=existing["id"],
            email=existing["email"],
            full_name=existing["full_name"],
            avatar_url=existing.get("avatar_url"),
            provider="guest",
            created_at=existing["created_at"]
        )
    else:
        user_id = f"usr_guest_{uuid.uuid4().hex[:8]}"
        user = repository.create_user(
            user_id=user_id,
            email=guest_email,
            full_name="Visionary Engineer (Guest)",
            password_hash=None,
            provider="guest",
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=guest_engineer&backgroundColor=8a2be2",
            created_at=now
        )

    token = create_jwt_token(user.id, user.email)
    stats = repository.get_user_stats(user.id)
    return AuthTokenResponse(
        access_token=token,
        user=user,
        stats=stats
    )

@router.get("/me")
def get_me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    token = authorization.split("Bearer ")[1].strip()
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    user = repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stats = repository.get_user_stats(user.id)
    return {
        "user": user,
        "stats": stats
    }
