from datetime import timedelta, datetime
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from sqlmodel import Session
import uuid

from models import User
from database import get_session


load_dotenv()  # Load environment variables from .env

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRE_MINUTES = 1440 # 24 hours by default

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Verify the password hash against the plaintext password
def verify_hash(plaintext_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plaintext_password, hashed_password)
    
# Create a password hash from the plaintext password
def create_hash(plaintext_password: str) -> str:
        return bcrypt.hash(plaintext_password)

# Create a JWT token with expiration time of 24 hours by default or custom time
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = uuid.UUID(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user_id
