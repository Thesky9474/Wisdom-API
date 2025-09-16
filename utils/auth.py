from datetime import datetime, timedelta
from typing import Optional
import os
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

# =========================================================
# CONFIG
# =========================================================
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

auth_scheme = HTTPBearer(auto_error=False)  # allow guest access


# =========================================================
# SCHEMAS
# =========================================================
class TokenData(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None


# =========================================================
# TOKEN CREATION
# =========================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =========================================================
# USER VALIDATION
# =========================================================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Force auth required → raise 401 if missing/invalid"""
    if not credentials:
        return None

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
        }
    except JWTError:
        return None


def optional_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Allow both guest and authenticated users"""
    if not credentials:
        return None  # Guest mode

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "username": payload.get("username"),
        }
    except JWTError:
        return None
