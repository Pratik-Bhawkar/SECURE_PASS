from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_user_db
from app.core.models import User
from app.core.security import get_current_user, require_role
from pydantic import BaseModel
import logging
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

def create_access_token(username: str):
    return f"token_{username}"

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_user_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        logger.error(f"Login failed: User {form_data.username} not found")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if user.hashed_password != form_data.password:
        logger.error(f"Login failed: Incorrect password for user {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(form_data.username)
    logger.info(f"User {form_data.username} logged in successfully")
    return {"access_token": access_token, "role": user.role, "token_type": "bearer"}

@router.post("/register")
async def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(require_role("manager"))
):
    # Extract fields from the request body
    username = request.username
    password = request.password
    role = request.role

    # Log the incoming data for debugging
    logger.debug(f"Received request body - username: {username}, password: {password}, role: {role}")

    # Normalize role to lowercase for comparison
    role = role.lower()
    logger.debug(f"Attempting to register user with role: {role}")

    if role not in ["admin", "security", "manager"]:
        logger.error(f"Invalid role during registration: {role}")
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.error(f"Registration failed: Username {username} already exists")
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=username, hashed_password=password, role=role)
    db.add(user)
    db.commit()
    logger.info(f"User {username} registered successfully with role {role}")
    return {"message": "User registered successfully"}