from datetime import timedelta, datetime
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends, Request
from dotenv import load_dotenv
import os
from sqlmodel import Session, select
import uuid

from models import AuthSession
from database import get_session


load_dotenv()  # Load environment variables from .env

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 # 1 hour by default

# Verify the password hash against the plaintext password
def verify_hash(plaintext_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plaintext_password, hashed_password)
    
# Create a password hash from the plaintext password
def create_hash(plaintext_password: str) -> str:
        return bcrypt.hash(plaintext_password)

async def create_session(user_id: uuid.UUID, session: Session = Depends(get_session)):
    newAuthSession = AuthSession(user_id=user_id, expires_at=datetime.now() + timedelta(minutes=EXPIRE_MINUTES))
    
    session.add(newAuthSession)
    session.commit()
    session.refresh(newAuthSession)
    
    return newAuthSession.id

async def validate_session(request: Request, session: Session = Depends(get_session)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
    
    existingAuthSession = session.exec(select(AuthSession)
                            .where(AuthSession.id == uuid.UUID(session_id))
                            .where(AuthSession.expires_at > datetime.now())
    ).first()
    
    if not existingAuthSession:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
    
    return existingAuthSession.user_id