import os
import tempfile
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.utils import detection_utils, ocr_utils
from app.core.models import User
from app.core.security import get_current_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ocr")
async def detect_and_ocr(
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "security":
        logger.error(f"User {current_user.username} with role {current_user.role} not authorized to extract plates")
        raise HTTPException(status_code=403, detail="Only security users can extract plates")

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    suffix = os.path.splitext(image.filename or "")[1].lower()
    if suffix not in valid_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {suffix}. Use {', '.join(valid_extensions)}")
    
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = await image.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name

        try:
            detections = detection_utils.detect_number_plate(temp_file_path)
        except Exception as e:
            logger.error(f"Error in detection for {image.filename} by user {current_user.username}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
        
        ocr_results = []
        if not detections:
            logger.info(f"No number plates detected in {image.filename} by user {current_user.username}")
            return {"status": "success", "ocr_results": []}

        for detection in detections:
            bbox = detection.get("bbox")
            if not bbox or len(bbox) != 4:
                logger.warning(f"Invalid bbox in detection for {image.filename} by user {current_user.username}: {bbox}")
                continue
            
            try:
                cropped = ocr_utils.crop_image(temp_file_path, bbox)
            except Exception as e:
                logger.error(f"Error cropping image for {image.filename}, bbox {bbox} by user {current_user.username}: {str(e)}")
                continue
            
            try:
                details = ocr_utils.get_plate_details(cropped, debug=True)
                plate_text = details['plate_text']
                ocr_confidence = details['confidence']
                is_valid = details['valid']
                
                original_conf = detection.get("confidence", 0.0)
                adjusted_conf = original_conf + 0.1 if is_valid else original_conf
                
                ocr_results.append({
                    "bbox": bbox,
                    "detection_confidence": original_conf,
                    "ocr_confidence": ocr_confidence,
                    "adjusted_confidence": adjusted_conf,
                    "class": detection.get("class", "number_plate"),
                    "text": plate_text,
                    "valid": is_valid
                })
                logger.info(f"Processed plate for {image.filename} by user {current_user.username}: {plate_text}, valid={is_valid}, conf={ocr_confidence}")
            except Exception as e:
                logger.error(f"Error in OCR for {image.filename}, bbox {bbox} by user {current_user.username}: {str(e)}")
                continue
        
        return {"status": "success", "ocr_results": ocr_results}
    
    except Exception as e:
        logger.error(f"Unexpected error processing {image.filename} by user {current_user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file_path} by user {current_user.username}: {str(e)}")