from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Existing schemas (from users.py)
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    hashed_password: str

    class Config:
        orm_mode = True

# New schemas for vehicles
class VehicleCreate(BaseModel):
    plate_number: str
    owner_name: str
    vehicle_type: str

class Vehicle(BaseModel):
    plate_number: str
    owner_name: str
    vehicle_type: str
    added_at: datetime

    class Config:
        orm_mode = True