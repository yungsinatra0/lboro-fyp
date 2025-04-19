from datetime import timedelta, datetime
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends, Request
from sqlmodel import Session, select
import uuid

from ..models import AuthSession
from .database import get_session

EXPIRE_MINUTES = 60 # 1 hour by default

def verify_hash(plaintext_password: str, hashed_password: str) -> bool:
    """
    Verify the password hash against the plaintext password.
    
    Args:
        plaintext_password: The plaintext password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    return bcrypt.verify(plaintext_password, hashed_password)
    
def create_hash(plaintext_password: str) -> str:
    """
    Create a password hash from the plaintext password.
    
    Args:
        plaintext_password: The plaintext password to hash
        
    Returns:
        str: The hashed password
    """
    return bcrypt.hash(plaintext_password)

async def create_session(user_id: uuid.UUID, session: Session = Depends(get_session)):
    """
    Create a new authentication session for the user.
    
    Args:
        user_id: UUID of the user to create a session for
        session: Database session dependency
        
    Returns:
        UUID: The ID of the newly created session
        
    Raises:
        HTTPException: If there's an error creating the session
    """
    newAuthSession = AuthSession(user_id=user_id, expires_at=datetime.now() + timedelta(minutes=EXPIRE_MINUTES))
    
    try:
        session.add(newAuthSession)
        session.commit()
        session.refresh(newAuthSession)
        
        return newAuthSession.id
    except Exception as e:
        session.rollback()
        print(f"Error creating session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when creating the session: {e}")

async def validate_session(request: Request, session: Session = Depends(get_session)):
    """
    Validate the user's session and return the user_id.
    Used as a dependency for protected routes.
    
    Args:
        request: The FastAPI request object containing cookies
        session: Database session dependency
        
    Returns:
        UUID: The ID of the user with a valid session
        
    Raises:
        HTTPException: If the session is invalid or expired
    """
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

async def end_session(request: Request, session: Session = Depends(get_session)):
    """
    End the user's session in the database.
    Note: This doesn't remove the cookie from the client.
    Used by the logout endpoint.
    
    Args:
        request: The FastAPI request object containing cookies
        session: Database session dependency
        
    Raises:
        HTTPException: If the session can't be found or deleted
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session cookie not found")
    
    existingAuthSession = session.exec(select(AuthSession)
                            .where(AuthSession.id == uuid.UUID(session_id))
    ).first()
    
    if not existingAuthSession:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session not found")
    try:
        session.delete(existingAuthSession)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error deleting session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when deleting the session: {e}")