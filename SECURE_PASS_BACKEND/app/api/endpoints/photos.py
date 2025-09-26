from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_photo_db
from app.core.models import Photo, User
from app.core.security import get_current_user
from pydantic import BaseModel
import logging
import re
import base64
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

def validate_plate(plate_number: str) -> bool:
    return bool(re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{1,4}$|^[A-Z]{2}\d{3,5}$', plate_number))

def validate_base64(data: str) -> bool:
    try:
        base64.b64decode(data, validate=True)
        return True
    except Exception:
        return False

class PhotoCreate(BaseModel):
    plate_number: str
    image_data: str

    class Config:
        schema_extra = {
            "example": {
                "plate_number": "MH12MB8677",
                "image_data": "/9j/4AAQSkZJRgABAQEAAAAAAAD/2wBDAA..."
            }
        }

class PhotoResponse(BaseModel):
    id: int
    plate_number: str
    image_data: str
    timestamp: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

@router.post("/", response_model=PhotoResponse)
async def upload_photo(
    photo: PhotoCreate,
    db: Session = Depends(get_photo_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to upload photos")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to upload photos")
        raise HTTPException(status_code=403, detail="Only security users can upload photos")

    try:
        if not validate_plate(photo.plate_number):
            logger.error(f"Invalid plate format: {photo.plate_number}")
            raise HTTPException(status_code=400, detail="Invalid plate format. Use formats like MH12MB8677, GJ01XY1234, or JK12345.")

        if not validate_base64(photo.image_data):
            logger.error(f"Invalid base64 image data for plate: {photo.plate_number}")
            raise HTTPException(status_code=400, detail="Invalid base64 image data.")

        max_length = 6_666_665  # Approx 5MB
        if len(photo.image_data) > max_length:
            logger.error(f"Image too large for plate: {photo.plate_number}, size: {len(photo.image_data)} chars")
            raise HTTPException(status_code=400, detail="Image size exceeds 5MB limit.")

        db_photo = Photo(
            plate_number=photo.plate_number,
            image_data=photo.image_data,
            timestamp=datetime.utcnow()
        )
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)

        logger.info(f"Photo uploaded for plate: {photo.plate_number}, id: {db_photo.id} by user {current_user.username}")
        return db_photo

    except Exception as e:
        logger.error(f"Error uploading photo for plate {photo.plate_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")

@router.get("/", response_model=list[PhotoResponse])
async def list_photos(
    db: Session = Depends(get_photo_db),
    current_user: Optional[User] = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    plate_number: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    if not current_user:
        logger.error("Authentication required to view photos")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "manager":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to view photos")
        raise HTTPException(status_code=403, detail="Only managers can view photos")

    try:
        query = db.query(Photo)

        if plate_number:
            if not validate_plate(plate_number):
                logger.error(f"Invalid plate format in filter: {plate_number}")
                raise HTTPException(status_code=400, detail="Invalid plate format in filter.")
            query = query.filter(Photo.plate_number == plate_number)

        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                query = query.filter(Photo.timestamp >= start)
            except ValueError:
                logger.error(f"Invalid start_date format: {start_date}")
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO 8601 (e.g., 2025-05-15).")

        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                query = query.filter(Photo.timestamp <= end)
            except ValueError:
                logger.error(f"Invalid end_date format: {end_date}")
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO 8601 (e.g., 2025-05-15).")

        photos = query.offset(offset).limit(limit).all()
        logger.info(f"User {current_user.username} retrieved {len(photos)} photos with limit={limit}, offset={offset}")
        return photos

    except Exception as e:
        logger.error(f"Error retrieving photos for user {current_user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve photos: {str(e)}")