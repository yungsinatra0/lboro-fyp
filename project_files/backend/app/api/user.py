from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session
import uuid

from ..models import User, UserResponse, UserUpdate, UserPasswordChange
from ..utils import get_session, validate_session, verify_hash, create_hash, limiter

router = APIRouter()

# Get current user info endpoint
@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_users_me(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Retrieve information about the currently logged in user.
    
    This endpoint is used by some backend functions to get the logged in user's information.

    Args:
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically 
            used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access 
            the database by using the SQLModel ORM.

    Raises:
        HTTPException: 401 UNAUTHORIZED if no valid session exists (handled by validate_session dependency).

    Returns:
        UserResponse: Object containing the user's profile information:
            - id: UUID: ID of the user
            - name: str: Name of the user
            - email: str: Email of the user
            - dob: str: Date of birth of the user
        status: 200 OK: User information retrieved successfully
    """
    return session.get(User, user_id)

# Update user endpoint  
@router.patch("/update", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def update_user(request: Request, user_update: UserUpdate, session: Session = Depends(get_session), user_id: uuid.UUID = Depends(validate_session)):
    """ Update the currently logged in user's profile information.
    
    This endpoint allows users to update their profile information such as name, email, 
    and date of birth. It does not allow password updates, which must be done through the
    dedicated password update endpoint.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter 
            middleware to limit the number of requests from a single IP address.
        user_update (UserUpdate): Contains the updated user data with all fields as optional:
            name as str, email as EmailStr, dob as date.
        session (Session, optional): Session is automatically used by the endpoint to access 
            the database by using the SQLModel ORM.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically 
            used by the endpoint to get the user ID from the session cookie and validate for database access.

    Raises:
        HTTPException: 404 NOT FOUND if the user is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID to be updated.
        HTTPException: 400 BAD REQUEST if an attempt is made to update the password using this endpoint.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs during the update process.

    Returns:
        "message": User updated successfully
        status: 200 OK: User information updated successfully
    """
    # Find the user to be updated, if not found, raise an exception
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_id != user_db.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this user")
    
    # Get the user data to be updated
    user_data = user_update.model_dump(exclude_unset=True)
    extra_data = {}
    
    # If password is being updated, hash it before updating
    if "password" in user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be updated using this endpoint")
    
    # Update the user data
    try:
        user_db.sqlmodel_update(user_data, update=extra_data)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        
        return {"message": "User updated successfully"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred when updating: {e}")    
    
# Update user password endpoint
@router.patch("/update/password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def update_password(password_update: UserPasswordChange, request: Request, response: Response, session: Session = Depends(get_session), user_id: uuid.UUID = Depends(validate_session)):
    """ Update the password for the currently logged in user.
    
    This endpoint handles password changes by verifying the current password before allowing
    the update to a new password. This provides security by ensuring only the actual user
    who knows the current password can change it.

    Args:
        password_update (UserPasswordChange): Contains password change data:
            - current_password: str: The user's current password for verification
            - new_password: str: The new password to set
        request (Request): Request is automatically used by the endpoint and the rate limiter 
            middleware to limit the number of requests from a single IP address.
        response (Response): Response object for the HTTP response
        session (Session, optional): Session is automatically used by the endpoint to access 
            the database by using the SQLModel ORM.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically 
            used by the endpoint to get the user ID from the session cookie and validate for database access.

    Raises:
        HTTPException: 404 NOT FOUND if the user is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID to be updated.
        HTTPException: 409 CONFLICT if the current password provided is incorrect.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs during the password update.

    Returns:
        "message": Password updated successfully
        status: 200 OK: Password updated successfully
    """
    user_db = session.get(User, user_id)
    
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_id != user_db.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this user")
    
    user_data = password_update.model_dump(exclude_unset=True)

    if not verify_hash(user_data["current_password"], user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect current password")
    
    user_db.hashed_password = create_hash(user_data["new_password"])
    
    try:
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        
        return {
            "message": "Password updated successfully"
        }
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred when updating: {e}")