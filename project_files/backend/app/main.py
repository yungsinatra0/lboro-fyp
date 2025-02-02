from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import uuid

# local imports
from database import create_db_and_tables, get_session
from models import UserAuth, User, UserUpdate, UserResponse

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

# Login endpoint
@app.post("/login")
def login(*, session: Session = Depends(get_session), login_data: UserAuth):
    user_db = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # Check if user exists
    if not user_db: 
        raise HTTPException(status_code=401, detail="Incorrect email or user does not exist")
    
    # Check if password is correct
    if user_db.verify_hash(login_data.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return {"message": "Login successful"} # TODO: Will need to change this later to return a token

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
            hashed_password=User.create_hash(register_data.password))
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
    
        return {"message": "Registration successfulasda"} # TODO: Will need to change this later to return a token or something
    
    # Unlikely to happen, but if an error occurs, rollback the transaction and raise an exception
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred when registering: {e}")

# Update user endpoint - TODO: Add authentication to this endpoint   
@app.patch("/update")
def update_user(*, session: Session = Depends(get_session), user_update: UserUpdate, user_id: uuid.UUID):
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
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user_db = session.get(User, user_id)
    
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_db