from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import uuid

# local imports
from database import create_db_and_tables, get_session
from models import UserAuth, User, UserUpdate, UserPublic, UserResponse, Token
from auth_utils import verify_hash, create_hash, create_session, validate_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try creating the database and tables, if not raise an exception
    try:
        create_db_and_tables()
        print("Database and tables created successfully")
    except Exception as e:
        print(f"Error creating database and tables: {e}")
    yield
        
app = FastAPI(lifespan=lifespan)

# PUBLIC ROUTES
# Login endpoint
@app.post("/login")
async def login(*, session: Session = Depends(get_session), login_data: UserAuth):
    user_db = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # Check if user exists
    if not user_db: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or user does not exist")
    
    # Check if password is correct
    if verify_hash(login_data.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    # Create a session for the user
    session_id = await create_session(user_db.id)
    
    # Set the session cookie
    Response.set_cookie(
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
@app.post("/register")
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


# PROTECTED ROUTES
# Get current user info endpoint
@app.get("/users/me", response_model=UserResponse)
async def read_users_me(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    return session.get(User, user_id)

# Update user endpoint - TODO: Add authentication to this endpoint   
@app.patch("/update", response_model=UserResponse)
def update_user(*, session: Session = Depends(get_session), user_update: UserUpdate, user_id: uuid.UUID = Depends(validate_session)):
    # Find the user to be updated, if not found, raise an exception
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the user data to be updated
    user_data = user_update.model_dump(exclude_unset=True)
    extra_data = {}
    
    # If password is being updated, hash it before updating
    if "password" in user_data:
        extra_data["hashed_password"] = User.create_hash(user_data["password"]) # Do I need to pop this from user_data?
    
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

# Get user info endpoint
@app.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: uuid.UUID, session: Session = Depends(get_session), current_user_id: uuid.UUID = Depends(validate_session)):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this user's data") # TODO: Change this to include admin access maybe?
      
    user_db = session.get(User, user_id)
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_db

# Homepage/dashboard endpoint
@app.get("/")
async def get_dashboard(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return {
        "message": f"Welcome {user.name}!"
        }