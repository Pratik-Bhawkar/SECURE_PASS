import base64
import cv2
import numpy as np
import logging
import os
from io import BytesIO
from datetime import datetime
from app.utils.ocr_utils import get_plate_details, correct_rotation

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def process_image(base64_image: str) -> dict:
    """
    Process a base64-encoded image to detect a license plate using ocr_utils.
    
    Args:
        base64_image: Base64-encoded string of the image
        
    Returns:
        Dictionary containing the detected plate number, confidence, and processed image
    """
    try:
        # Log the start of processing with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.debug(f"Processing image at timestamp {timestamp}, base64 length: {len(base64_image)}")

        # Decode base64 image
        try:
            image_data = base64.b64decode(base64_image)
        except base64.binascii.Error as e:
            logger.error(f"Invalid base64 encoding: {str(e)}")
            return {
                "plate_number": "Not detected",
                "confidence": 0.0,
                "image": base64_image,
                "error": "Invalid base64 encoding"
            }
        except Exception as e:
            logger.error(f"Unexpected error decoding base64: {str(e)}")
            return {
                "plate_number": "Not detected",
                "confidence": 0.0,
                "image": base64_image,
                "error": "Base64 decoding failed"
            }

        # Convert to NumPy array and decode to OpenCV image
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Failed to decode image into OpenCV format")
            return {
                "plate_number": "Not detected",
                "confidence": 0.0,
                "image": base64_image,
                "error": "Failed to decode image"
            }

        # Validate image dimensions
        height, width = image.shape[:2]
        if height < 50 or width < 50:
            logger.warning(f"Image too small for processing: {width}x{height}")
            return {
                "plate_number": "Not detected",
                "confidence": 0.0,
                "image": base64_image,
                "error": "Image too small"
            }
        logger.debug(f"Decoded image dimensions: {width}x{height}")

        # Save the original image for debugging
        debug_dir = "debug_images"
        os.makedirs(debug_dir, exist_ok=True)
        debug_image_path = os.path.join(debug_dir, f"input_{timestamp}.jpg")
        cv2.imwrite(debug_image_path, image)
        logger.debug(f"Saved input image to {debug_image_path}")

        # Preprocess the image: resize and correct rotation
        # Resize to a standard width (maintaining aspect ratio) for consistency
        target_width = 640
        aspect_ratio = target_width / width
        target_height = int(height * aspect_ratio)
        image_resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
        logger.debug(f"Resized image to {target_width}x{target_height}")

        # Correct rotation using the utility from ocr_utils
        image_rotated = correct_rotation(image_resized)
        cv2.imwrite(os.path.join(debug_dir, f"rotated_{timestamp}.jpg"), image_rotated)
        logger.debug(f"Saved rotated image to debug/rotated_{timestamp}.jpg")

        # Use ocr_utils to detect the license plate
        result = get_plate_details(image_rotated, debug=True, apply_rotation=False)
        plate_number = result["plate_text"]
        confidence = result["confidence"]
        is_valid = result["valid"]

        # Log the result
        if not plate_number or not is_valid:
            logger.warning(f"No valid license plate detected. Raw OCR: {result['raw_text']}")
            plate_number = "Not detected"
            confidence = 0.0
        else:
            logger.info(f"Detected plate: {plate_number} with confidence {confidence:.2f}, valid: {is_valid}")

        # Annotate the image with the detected plate number
        output_image = image_rotated.copy()
        if plate_number != "Not detected":
            # Add text at the top-left corner
            cv2.putText(
                output_image,
                f"Plate: {plate_number}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),  # Green text
                2
            )
            cv2.putText(
                output_image,
                f"Conf: {confidence:.2f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 200, 255),  # Yellow text
                2
            )

        # Encode the annotated image back to base64
        _, buffer = cv2.imencode('.jpg', output_image, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        base64_image_return = base64.b64encode(buffer).decode('utf-8')

        # Save the annotated image for reference
        annotated_image_path = os.path.join(debug_dir, f"annotated_{timestamp}.jpg")
        cv2.imwrite(annotated_image_path, output_image)
        logger.debug(f"Saved annotated image to {annotated_image_path}")

        return {
            "plate_number": plate_number,
            "confidence": confidence,
            "image": base64_image_return,
            "error": None
        }

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        return {
            "plate_number": "Not detected",
            "confidence": 0.0,
            "image": base64_image,
            "error": f"Processing failed: {str(e)}"
        }