from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session
import uuid

from ..models import User, UserResponse, UserUpdate, UserPasswordChange
from ..utils import get_session, validate_session, verify_hash, create_hash

router = APIRouter()

# Get current user info endpoint
@router.get("/me", response_model=UserResponse)
async def read_users_me(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    return session.get(User, user_id)

# Update user endpoint  
@router.patch("/update", response_model=UserResponse)
def update_user(*, session: Session = Depends(get_session), user_update: UserUpdate, user_id: uuid.UUID = Depends(validate_session)):
    # Find the user to be updated, if not found, raise an exception
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id != user_db.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this user")
    
    # Get the user data to be updated
    user_data = user_update.model_dump(exclude_unset=True)
    extra_data = {}
    
    # If password is being updated, hash it before updating
    if "password" in user_data:
        raise HTTPException(status_code=400, detail="Password cannot be updated using this endpoint")
    
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
@router.patch("/update/password")
def update_password(*, request: Request, session: Session = Depends(get_session), password_update: UserPasswordChange, response: Response, user_id: uuid.UUID = Depends(validate_session)):
    user_db = session.get(User, user_id)
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id != user_db.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this user")
    
    user_data = password_update.model_dump(exclude_unset=True)

    if not verify_hash(user_data["current_password"], user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect current password")
    
    user_db.hashed_password = create_hash(user_data["new_password"])
    
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Password updated successfully"
    } 