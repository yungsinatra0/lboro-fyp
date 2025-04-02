from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api import auth_router, user_router, file_router, vaccine_router, allergy_router, healthdata_router, medication_router, dashboard_router, medhistory_router, labs_router
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

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(file_router)
app.include_router(vaccine_router)
app.include_router(allergy_router)
app.include_router(healthdata_router)
app.include_router(medication_router)
app.include_router(dashboard_router)
app.include_router(medhistory_router)
app.include_router(labs_router)