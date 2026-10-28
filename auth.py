"""
Authentication & Session Management Service for Habit CRM
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import config
from database import get_db
from models import User

# JWT Settings
JWT_SECRET = config.SECRET_KEY
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
SESSION_COOKIE_NAME = "habit_crm_session"

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hashes a password with bcrypt and a unique salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a signed JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None

def extract_token(request: Request, auth_header: Optional[HTTPAuthorizationCredentials] = None) -> Optional[str]:
    """Extracts JWT token from Authorization header or HTTP-only session cookie."""
    if auth_header and auth_header.credentials:
        return auth_header.credentials
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        return cookie_token
    return None

def get_current_user_optional(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Returns the authenticated user or None if unauthenticated."""
    token = extract_token(request, auth_header)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    user_id = payload.get("sub")
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    return user

def get_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency: Enforces that the request has a valid authenticated user."""
    user = get_current_user_optional(request, auth_header, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# ========================================================
# IP-based Rate Limiting for Abuse Prevention
# ========================================================
import time
from collections import defaultdict

_rate_limits = defaultdict(lambda: defaultdict(list))

def check_rate_limit(request: Request, action: str = "auth", max_attempts: int = 15, window_seconds: int = 60):
    """
    Enforces IP-based rate limiting for sensitive endpoints (e.g. login, register).
    Raises HTTPException(429) if exceeded.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    attempts = _rate_limits[action][client_ip]
    
    # Filter out attempts older than window
    _rate_limits[action][client_ip] = [t for t in attempts if now - t < window_seconds]
    
    if len(_rate_limits[action][client_ip]) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many {action} attempts. Please wait a minute before trying again."
        )
    
    _rate_limits[action][client_ip].append(now)

