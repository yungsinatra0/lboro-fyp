from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)   

def create_db_and_tables():
    """
    Create the database and tables at application startup.
    
    This function is called in the main app file to create 
    the database and tables if they don't exist yet.
    """
    SQLModel.metadata.create_all(engine)
    
def get_session():
    """
    Dependency function to get a database session.
    
    Used by all endpoints that require database operations with SQLModel.
    
    Yields:
        Session: A SQLModel session for database operations
    """
    with Session(engine) as session:
        yield session