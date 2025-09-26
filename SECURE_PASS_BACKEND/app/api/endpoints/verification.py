from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models import AuthorizedVehicle, AccessLog, User
from app.core.security import get_current_user
from datetime import datetime
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def validate_plate(plate_number: str) -> bool:
    return bool(re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{1,4}$|^[A-Z]{2}\d{3,5}$', plate_number))

class VerifyRequest(BaseModel):
    plate_number: str
    confidence: float

@router.post("/verify")
async def verify_plate(
    request: VerifyRequest,
    db: Session = Depends(SessionLocal),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to verify vehicles")
        raise HTTPException(status_code=403, detail="Only security users can verify vehicles")

    try:
        plate_number = request.plate_number
        confidence = request.confidence

        if not validate_plate(plate_number):
            logger.error(f"Invalid plate format: {plate_number}")
            raise HTTPException(status_code=400, detail="Invalid plate format. Use formats like MH12MB8677, GJ01XY1234, or JK12345.")

        vehicle = db.query(AuthorizedVehicle).get(plate_number)
        authorized = vehicle is not None

        log = AccessLog(
            plate_number=plate_number,
            timestamp=datetime.utcnow(),
            confidence=confidence,
            authorized=authorized
        )
        db.add(log)
        db.commit()
        logger.info(f"Verification logged by user {current_user.username}: {plate_number}, authorized={authorized}, confidence={confidence}")

        return {"authorized": authorized}
    except Exception as e:
        logger.error(f"Error verifying plate {plate_number} for user {current_user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
    finally:
        db.close()