from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import detection, ocr, verification, vehicles, users, logs, photos
from app.core.database import init_db
from app.core.config import HOST, PORT, DEBUG, LOG_LEVEL
import logging
import os

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Secure Pass API",
    description="License Plate Recognition and Access Control System",
    version="1.0.0"
)

# CORS configuration - Allow all origins in development, specific origins in production
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add environment-specific origins
if os.getenv("ALLOWED_ORIGINS"):
    allowed_origins.extend(os.getenv("ALLOWED_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Call init_db on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(detection.router, prefix="/detection", tags=["Detection"])
app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(verification.router, prefix="/verify", tags=["Verification"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(users.router, tags=["Users"])  # No prefix for auth endpoints
app.include_router(logs.router, prefix="/logs", tags=["Logs"])
app.include_router(photos.router, prefix="/photos", tags=["photos"])

@app.get("/")
async def root():
    return {"message": "Welcome to SECURE PASS BACKEND"}