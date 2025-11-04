import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./secure_pass.db")
DATABASE_PATH = PROJECT_ROOT / os.getenv("DATABASE_PATH", "secure_pass.db")

# Application configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-very-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Data directories (relative to project root)
DATA_DIR = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
RAW_DATA_DIR = PROJECT_ROOT / os.getenv("RAW_DATA_DIR", "data/raw")
CLEANED_DATA_DIR = PROJECT_ROOT / os.getenv("CLEANED_DATA_DIR", "data/cleaned")
TRASH_DATA_DIR = PROJECT_ROOT / os.getenv("TRASH_DATA_DIR", "data/trash")
VALID_PLATES_DIR = PROJECT_ROOT / os.getenv("VALID_PLATES_DIR", "data/VALID_PLATES")
CUSTOM_DATASET_DIR = PROJECT_ROOT / os.getenv("CUSTOM_DATASET_DIR", "data/custom_dataset")
DEBUG_DIR = PROJECT_ROOT / os.getenv("DEBUG_DIR", "debug")

# Model configuration
YOLO_MODEL_PATH = PROJECT_ROOT / os.getenv("YOLO_MODEL_PATH", "yolo_v8_custom_updated/weights/best.pt")

# File upload configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,bmp").split(",")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / os.getenv("LOG_FILE", "logs/secure_pass.log")

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        DATA_DIR, RAW_DATA_DIR, CLEANED_DATA_DIR, TRASH_DATA_DIR,
        VALID_PLATES_DIR, CUSTOM_DATASET_DIR, DEBUG_DIR,
        LOG_FILE.parent
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Create directories on import
ensure_directories()