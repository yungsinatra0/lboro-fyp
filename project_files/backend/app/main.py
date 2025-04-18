from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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

# Middleware to compress responses for larger payloads
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set a trusted host list for incoming requests to prevent host header attacks
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=[
        "localhost", 
        "localhost:8000",
        "127.0.0.1",
        "127.0.0.1:8000"
    ]
)

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# HTTPS redirect middleware to redirect HTTP requests to HTTPS
# Will be enabled in production
# app.add_middleware(HTTPSRedirectMiddleware)

for router in get_all_routers():
    app.include_router(router)