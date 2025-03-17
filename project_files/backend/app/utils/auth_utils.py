from datetime import timedelta, datetime
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends, Request
from sqlmodel import Session, select
import uuid

from ..models import AuthSession
from .database import get_session

EXPIRE_MINUTES = 60 # 1 hour by default

# Util function to verify the password hash against the plaintext password
def verify_hash(plaintext_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plaintext_password, hashed_password)
    
# Util function to create a password hash from the plaintext password
def create_hash(plaintext_password: str) -> str:
        return bcrypt.hash(plaintext_password)


# Util function to create a new session for the user
async def create_session(user_id: uuid.UUID, session: Session = Depends(get_session)):
    newAuthSession = AuthSession(user_id=user_id, expires_at=datetime.now() + timedelta(minutes=EXPIRE_MINUTES))
    
    session.add(newAuthSession)
    session.commit()
    session.refresh(newAuthSession)
    
    return newAuthSession.id

# Util function to validate the session and return the user_id - also used as a dependency for protected routes
async def validate_session(request: Request, session: Session = Depends(get_session)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session cookie not found")
    
    existingAuthSession = session.exec(select(AuthSession)
                            .where(AuthSession.id == uuid.UUID(session_id))
                            .where(AuthSession.expires_at > datetime.now())
    ).first()
    
    if not existingAuthSession:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")  
    
    return existingAuthSession.user_id

# Util function to end the session in the database (doesn't remove the cookie from the client)
async def end_session(request: Request, session: Session = Depends(get_session)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session cookie not found")
    
    existingAuthSession = session.exec(select(AuthSession)
                            .where(AuthSession.id == uuid.UUID(session_id))
    ).first()
    
    if not existingAuthSession:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
    
    session.delete(existingAuthSession)
    session.commit()
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Session ended"
    }