from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_user_db
from app.core.models import AuthorizedVehicle, AccessLog, User
from app.core.schemas import VehicleCreate, Vehicle
from app.core.security import get_current_user
from pydantic import BaseModel
import re
import logging
import subprocess
import json
from datetime import datetime
from typing import Optional
from app.scripts.mobile_image_processor import process_image  # Import the new processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class VerifyRequest(BaseModel):
    plate_number: str
    confidence: float

class MobileCaptureRequest(BaseModel):
    image: str  # Base64-encoded image

def validate_plate(plate_number: str) -> bool:
    return bool(re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{1,4}$|^[A-Z]{2}\d{3,5}$', plate_number))

@router.post("/verify", response_model=dict)
async def verify_vehicle(
    request: VerifyRequest,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to verify vehicles")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to verify vehicles")
        raise HTTPException(status_code=403, detail="Only security users can verify vehicles")

    try:
        if not validate_plate(request.plate_number):
            logger.error(f"Invalid plate format: {request.plate_number}")
            raise HTTPException(status_code=400, detail="Invalid plate format")

        vehicle = db.query(AuthorizedVehicle).get(request.plate_number)
        authorized = vehicle is not None

        log_entry = AccessLog(
            plate_number=request.plate_number,
            timestamp=datetime.utcnow(),
            confidence=request.confidence,
            authorized=authorized
        )
        db.add(log_entry)
        db.commit()

        logger.info(f"Vehicle verified: {request.plate_number}, Authorized: {authorized} by user {current_user.username}")
        return {
            "plate_number": request.plate_number,
            "authorized": authorized
        }
    except Exception as e:
        logger.error(f"Error verifying vehicle {request.plate_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify vehicle: {str(e)}")

@router.post("/capture-mobile", response_model=dict)
async def capture_mobile(
    request: MobileCaptureRequest,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to capture mobile images")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to capture mobile images")
        raise HTTPException(status_code=403, detail="Only security users can capture mobile images")

    try:
        # Process the image to detect the plate
        result = process_image(request.image)
        plate_number = result["plate_number"]
        confidence = result["confidence"]
        image_base64 = result["image"]

        # Verify the plate against authorized vehicles
        vehicle = db.query(AuthorizedVehicle).get(plate_number)
        authorized = vehicle is not None

        # Log the access
        log_entry = AccessLog(
            plate_number=plate_number,
            timestamp=datetime.utcnow(),
            confidence=confidence,
            authorized=authorized
        )
        db.add(log_entry)
        db.commit()

        logger.info(f"Mobile image captured: Plate {plate_number}, Authorized: {authorized} by user {current_user.username}")
        return {
            "plate_number": plate_number,
            "confidence": confidence,
            "authorized": authorized,
            "image": image_base64
        }
    except Exception as e:
        logger.error(f"Error capturing mobile image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error capturing mobile image: {str(e)}")

@router.post("/capture-ip-webcam", response_model=dict)
async def capture_ip_webcam(
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to capture IP webcam images")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to capture IP webcam images")
        raise HTTPException(status_code=403, detail="Only security users can capture IP webcam images")

    try:
        result = subprocess.run(
            ["python", "app/scripts/ip_webcam.py"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"IP Webcam script failed: {result.stderr}")
            raise HTTPException(status_code=500, detail="Failed to capture image from IP Webcam")

        output = result.stdout.strip()
        result_data = json.loads(output.split("Result: ")[-1])
        logger.info(f"IP Webcam image captured by user {current_user.username}")
        return result_data
    except Exception as e:
        logger.error(f"Error capturing IP Webcam image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error capturing IP Webcam image: {str(e)}")

@router.post("/", status_code=201, response_model=dict)
async def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to add vehicles")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "admin":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to add vehicles")
        raise HTTPException(status_code=403, detail="Only admins can add vehicles")

    try:
        if not validate_plate(vehicle.plate_number):
            logger.error(f"Invalid plate format: {vehicle.plate_number}")
            raise HTTPException(status_code=400, detail="Invalid plate format. Use formats like MH12MB8677, GJ01XY1234, or JK12345.")
        
        if db.query(AuthorizedVehicle).get(vehicle.plate_number):
            logger.warning(f"Duplicate plate: {vehicle.plate_number}")
            raise HTTPException(status_code=400, detail="Plate already exists")
        
        db_vehicle = AuthorizedVehicle(
            plate_number=vehicle.plate_number,
            owner_name=vehicle.owner_name,
            vehicle_type=vehicle.vehicle_type
        )
        db.add(db_vehicle)
        db.commit()
        logger.info(f"Vehicle added: {vehicle.plate_number} by admin {current_user.username}")
        return {"message": "Vehicle added"}
    except Exception as e:
        logger.error(f"Error creating vehicle {vehicle.plate_number}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add vehicle: {str(e)}")

@router.get("/", response_model=list[Vehicle])
async def list_vehicles(
    db: Session = Depends(get_user_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    try:
        vehicles = db.query(AuthorizedVehicle).all()
        username = current_user.username if current_user else "anonymous"
        logger.info(f"User {username} retrieved {len(vehicles)} vehicles")
        return vehicles
    except Exception as e:
        username = current_user.username if current_user else "anonymous"
        logger.error(f"Error listing vehicles for user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list vehicles: {str(e)}")

@router.get("/{plate_number}", response_model=Vehicle)
async def get_vehicle(
    plate_number: str,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to retrieve vehicle details")
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        if not validate_plate(plate_number):
            logger.error(f"Invalid plate format: {plate_number}")
            raise HTTPException(status_code=400, detail="Invalid plate format")
        
        v = db.query(AuthorizedVehicle).get(plate_number)
        if not v:
            logger.warning(f"Vehicle not found: {plate_number}")
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        logger.info(f"User {current_user.username} retrieved vehicle: {plate_number}")
        return v
    except Exception as e:
        logger.error(f"Error retrieving vehicle {plate_number} for user {current_user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve vehicle: {str(e)}")

@router.delete("/{plate_number}", response_model=dict)
async def delete_vehicle(
    plate_number: str,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        logger.error("Authentication required to delete vehicles")
        raise HTTPException(status_code=401, detail="Authentication required")

    if current_user.role != "admin":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to delete vehicles")
        raise HTTPException(status_code=403, detail="Only admins can delete vehicles")

    try:
        if not validate_plate(plate_number):
            logger.error(f"Invalid plate format: {plate_number}")
            raise HTTPException(status_code=400, detail="Invalid plate format")
        
        v = db.query(AuthorizedVehicle).get(plate_number)
        if not v:
            logger.warning(f"Vehicle not found: {plate_number}")
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        db.delete(v)
        db.commit()
        logger.info(f"Vehicle deleted: {plate_number} by admin {current_user.username}")
        return {"message": "Vehicle deleted"}
    except Exception as e:
        logger.error(f"Error deleting vehicle {plate_number} for user {current_user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete vehicle: {str(e)}")