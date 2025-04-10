from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api import get_all_routers
from .utils import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try creating the database and tables before starting the API server (will not do anything if they already exist)
    try:
        create_db_and_tables()
        print("Database and tables created successfully")
    except Exception as e:
        print(f"Error creating database and tables: {e}")
    yield

# Initialize the FastAPI application
app = FastAPI(lifespan=lifespan)

for router in get_all_routers():
    app.include_router(router)