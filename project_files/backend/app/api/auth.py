from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select
import uuid

from ..models import User, UserAuth, AuthSession
from ..utils import get_session, validate_session, create_session, end_session, create_hash, verify_hash

router = APIRouter()

# PUBLIC ROUTES
# Login endpoint
@router.post("/login")
async def login(*, session: Session = Depends(get_session), login_data: UserAuth, response: Response):
    user_db = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # Check if user exists
    if not user_db: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or user does not exist")
    
    # Check if password is correct
    if not verify_hash(login_data.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    # Create a session for the user
    session_id = await create_session(user_db.id, session)
    
    # Set the session cookie in the response and send it to the client
    response.set_cookie(
        "session_id",
        str(session_id),
        httponly=True,
        max_age=3600,
        samesite="strict",
        secure=True
    )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Login successful",
        "user_id": user_db.id
    }    
    

# Register endpoint
@router.post("/register")
def register(*, session: Session = Depends(get_session), register_data: UserAuth):
    
    # Check if email is already registered
    if session.exec(select(User).where(User.email == register_data.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Try to register the user and add to database
    try:
        user_db = User(
            name = register_data.name,
            email = register_data.email, 
            dob = register_data.dob,
            hashed_password=create_hash(register_data.password))
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
    
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User registered successfully"
            }
    
    # Unlikely to happen, but if an error occurs, rollback the transaction and raise an exception
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when registering: {e}")


################# PROTECTED ROUTES
# Logout endpoint
@router.post("/logout")
async def logout(response: Response, request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    
    session_id = request.cookies.get("session_id")
    cookie_user_id = session.get(AuthSession, uuid.UUID(session_id)).user_id
    
    if cookie_user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to log out this user")
    
    print("\n Deleting sessiong from database \n")
    
    # Will use the end_session function to end the session in the database
    await end_session(request, session) # Need to pass the request and session to the function, otherwise it will not work
    
    # Still need to delete the session cookie from the client
    response.delete_cookie(
        "session_id",
        samesite="strict",
        secure=True,
        httponly=True
        )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Logout successful"
    }