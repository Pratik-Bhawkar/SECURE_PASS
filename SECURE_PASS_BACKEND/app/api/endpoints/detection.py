import os
import tempfile
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.utils import detection_utils
from app.core.models import User
from app.core.security import get_current_user
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def detect_number_plate(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to detect vehicles")
        raise HTTPException(status_code=403, detail="Only security users can detect vehicles")

    try:
        logger.info(f"NumPy version: {np.__version__}")
    except Exception as e:
        logger.error(f"NumPy import failed in detection.py for user {current_user.username}: {str(e)}")
        return {"status": "error", "message": f"NumPy check failed: {str(e)}"}

    suffix = os.path.splitext(image.filename)[1] if image.filename else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        contents = await image.read()
        temp_file.write(contents)
        temp_file_path = temp_file.name

    try:
        logger.info(f"Calling detection_utils.detect_number_plate with file: {temp_file_path} by user {current_user.username}")
        detections = detection_utils.detect_number_plate(temp_file_path)
    except Exception as e:
        os.remove(temp_file_path)
        logger.error(f"Detection failed for user {current_user.username}: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return {"status": "success", "detections": detections}