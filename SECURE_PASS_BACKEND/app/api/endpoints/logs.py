from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_user_db
from app.core.models import AccessLog
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AccessLogResponse(BaseModel):
    id: int
    plate_number: str
    timestamp: str
    confidence: float
    authorized: bool

    class Config:
        # Use orm_mode for Pydantic v1 compatibility (since project likely uses older FastAPI)
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

@router.get("/", response_model=list[AccessLogResponse])
async def list_logs(
    limit: int = Query(10, ge=1, le=100, description="Number of logs to return"),
    db: Session = Depends(get_user_db)
):
    try:
        # Fetch logs from the database
        logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).limit(limit).all()
        
        # Manually serialize the timestamp field to a string
        serialized_logs = [
            {
                "id": log.id,
                "plate_number": log.plate_number,
                "timestamp": log.timestamp.isoformat(),  # Convert datetime to ISO string
                "confidence": log.confidence,
                "authorized": log.authorized
            }
            for log in logs
        ]
        
        logger.info(f"Retrieved {len(serialized_logs)} access logs")
        return serialized_logs
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")