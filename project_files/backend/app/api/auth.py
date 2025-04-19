from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select
import uuid

from ..models import User, UserAuth, AuthSession
from ..utils import get_session, validate_session, create_session, end_session, create_hash, verify_hash
from ..utils import limiter

router = APIRouter()

# Login endpoint
@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def login(login_data: UserAuth, response: Response, request: Request, session: Session = Depends(get_session)):
    """ Login endpoint. Will be used to check the received credentials from login page and create a session for the user if they are correct.

    Args:
        login_data (UserAuth): Contains login data: email as EmailStr and password as str.
        response (Response): Response is automatically used by the endpoint to set the session cookie in the response.
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 401 UNAUTHORIZED if the email is wrong or the user does not exist.
        HTTPException: 401 UNAUTHORIZED if the password is wrong.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when creating the session.

    Returns:
        "message": Login successful,
        "user_id": UUID: User ID of the logged in user.
    """
    user_db = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # Check if user exists
    if not user_db: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or user does not exist")
    
    # Check if password is correct
    if not verify_hash(login_data.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    try:
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
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when creating the session: {e}")
    
    return {
        "message": "Login successful",
        "user_id": user_db.id
    }    
    

# Register endpoint
@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")
def register(register_data: UserAuth, request: Request, session: Session = Depends(get_session)):
    """ Register endpoint. Will be used to register a new user in the database. 

    Args:
        register_data (UserAuth): Contains register data: email as EmailStr, password as str and name as str.
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 409 CONFLICT if the email is already registered.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when registering the user.

    Returns:
        "message": User registered successfully
    """
    
    # Check if email is already registered
    if session.exec(select(User).where(User.email == register_data.email)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    # If not, try to register the user and add to database
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
            "message": "User registered successfully"
            }
    
    # Unlikely to happen, but if an error occurs, rollback the transaction and raise an exception
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when registering: {e}")


# Logout endpoint
@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def logout(response: Response, request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Logout endpoint. Will be used to log out the user by deleting the cookie in the frontend and delete the session from the database.

    Args:
        response (Response): Response is automatically used by the endpoint to delete the session cookie in the response.
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address, also to get the session ID from the cookie.
        user_id (uuid.UUID): User ID of the logged in user, received from the dependency injection. Used to check if the user is logged in and to check if the user is trying to log out their own session.
        session (Session): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 403 FORBIDDEN if the user id in the cookie does not match the user ID in the session.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when logging out the user.

    Returns:
        "message": Logout successful
    """
    
    # Get session ID from the cookie and check if it matches the user ID in the session
    session_id = request.cookies.get("session_id")
    cookie_user_id = session.get(AuthSession, uuid.UUID(session_id)).user_id
    
    if cookie_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to log out this user")
    
    try:
        # Will use the end_session function to end the session in the database
        await end_session(request, session) # Need to pass the request and session to the function, otherwise it will not work
        
        # Still need to delete the session cookie from the client
        response.delete_cookie(
            "session_id",
            samesite="strict",
            secure=True,
            httponly=True
            )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when logging out: {e}")
        
    return {
        "message": "Logout successful"
    }