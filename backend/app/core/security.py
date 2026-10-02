from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import get_settings
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto'); security = HTTPBearer(auto_error=False)
def hash_password(value: str) -> str: return pwd_context.hash(value)
def verify_password(value: str, hashed: str) -> bool: return pwd_context.verify(value, hashed)
def create_access_token(subject: str) -> str:
	s=get_settings(); return jwt.encode({'sub':subject,'exp':datetime.now(timezone.utc)+timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)},s.JWT_SECRET,algorithm=s.JWT_ALGORITHM)
def get_current_user(credentials: HTTPAuthorizationCredentials | None=Depends(security)) -> dict[str,Any]:
	if credentials is None: raise HTTPException(401, 'Authentication required')
	try: return jwt.decode(credentials.credentials,get_settings().JWT_SECRET,algorithms=[get_settings().JWT_ALGORITHM])
	except JWTError as exc: raise HTTPException(401,'Invalid or expired token') from exc
