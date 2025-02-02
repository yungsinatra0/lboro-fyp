from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager

# local imports
from database import create_db_and_tables, get_session
from models import UserAuth, User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database and tables
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/login")
def login(*, session: Session = Depends(get_session), login_data: UserAuth):
    user_db = session.exec(select(User).where(User.email == login_data.email)).first()
    if not user_db or not user_db.verify_hash(login_data.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    return {"message": "Login successful"}

@app.post("/register")
def register(*, session: Session = Depends(get_session), register_data: UserAuth):
    
    if session.exec(select(User).where(User.email == register_data.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_db = User(
        name = register_data.name,
        email = register_data.email, 
        dob = register_data.dob,
        hashed_password=User.create_hash(register_data.password))
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    
    return {"message": "Registration successfulasda"}