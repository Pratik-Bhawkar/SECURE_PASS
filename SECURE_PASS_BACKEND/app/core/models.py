from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, func
from app.core.database import Base
from datetime import datetime

# User management database models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # admin, security, manager
    created_at = Column(DateTime, default=datetime.utcnow)

# Authorized vehicles database models
class AuthorizedVehicle(Base):
    __tablename__ = "authorized_vehicles"
    plate_number = Column(String, primary_key=True, index=True)
    owner_name = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    added_at = Column(DateTime, default=func.now())

# Access logs database models
class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    confidence = Column(Float, nullable=False)
    authorized = Column(Boolean, nullable=False)

# Captured images database models
class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True)
    image_data = Column(String)  # Store base64 string
    timestamp = Column(DateTime, default=datetime.utcnow)