from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User, Role
from app.schemas.auth import LoginRequest, RegisterRequest
router = APIRouter()

@router.post('/login')
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(401, 'Invalid credentials')
    return {'access_token': create_access_token(str(user.id)), 'token_type': 'bearer', 'role': user.role.value, 'name': user.name}

@router.post('/register')
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first(): raise HTTPException(400, 'User already exists')
    user = User(name=payload.name, email=payload.email.lower(), phone=payload.phone, password_hash=hash_password(payload.password), role=Role.CUSTOMER)
    db.add(user); db.commit(); db.refresh(user)
    return {'access_token': create_access_token(str(user.id)), 'token_type': 'bearer', 'role': user.role.value, 'name': user.name}
