import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URLs
USER_DB_URL = "sqlite:///./user_management.db"
PHOTO_DB_URL = "sqlite:///./captured_images.db"

# Create engines
user_engine = create_engine(USER_DB_URL, connect_args={"check_same_thread": False})
photo_engine = create_engine(PHOTO_DB_URL, connect_args={"check_same_thread": False})

# Create session factories
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
PhotoSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=photo_engine)

# Generic SessionLocal (for compatibility with existing endpoints)
SessionLocal = UserSessionLocal  # Default to user database; adjust if needed

# Base class for models
Base = declarative_base()

def get_user_db():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_photo_db():
    db = PhotoSessionLocal()
    try:
        yield db
    finally:
        db.close()
# Import all models so they are registered with SQLAlchemy's Base
from app.core import models

def init_db():
    # Ensure all tables are created for both databases
    Base.metadata.create_all(bind=user_engine)
    Base.metadata.create_all(bind=photo_engine)