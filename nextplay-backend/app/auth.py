from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import JWTError
from app.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        decode = decode_access_token(token)
    except JWTError as e:
        raise HTTPException (
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "bad token"
        )
    email = decode["sub"]
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException (
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User not found"
        )
    return user