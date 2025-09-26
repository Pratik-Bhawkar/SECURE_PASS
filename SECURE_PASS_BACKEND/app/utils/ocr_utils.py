import cv2
import os
import re
import numpy as np
import logging
from paddleocr import PaddleOCR
from typing import List, Dict, Tuple, Union, Optional, Any

# Configure logging to match mobile_image_processor.py
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Optional: Install Tesseract for fallback OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("Tesseract not available. Install pytesseract for fallback OCR.")

# Initialize PaddleOCR model with optimized settings for license plates
paddle_ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    det_db_score_mode="fast",
    det_db_box_thresh=0.5,
    det_db_unclip_ratio=1.5,
    rec_batch_num=1,
    rec_char_type="en",
    use_space_char=False
)

# Patterns and constants for license plate processing
STATE_CODES: List[str] = ['MH']  # Restrict to MH only

# Enhanced character corrections with context-aware rules
CHAR_CORRECTIONS: Dict[str, str] = {
    '$': 'S',
    'I': '1',
    'B': '8',
    'D': '0',
    'Q': '0',
    'Z': '2',
    'S': '5',
    'l': '1',
    'G': '6',
    'T': '7',
    'E': '8',
    '0': 'O',  # Will be contextually adjusted
    'O': '0'   # Will be contextually adjusted
}

# IND removal patterns tailored for MH01OE1234 and MH1201 formats
IND_PATTERNS: List[str] = [
    r'(MH\d{2})IND([A-Z]{2}\d{4})',
    r'(MH\d{2}[A-Z]{2})IND(\d{4})',
    r'(MH)IND(\d{2}[A-Z]{2}\d{4})',
    r'(MH\d{2})I\s*N\s*D([A-Z]{2}\d{4})',
    r'(MH)IND(\d{3,5})'
]

# Unwanted text in license plates (expanded list)
UNWANTED_TEXT: List[str] = [
    "SCO", "OKULNAGAR", "ONDA", "METRO", "CO0DN", "GARDEN", "PUNE",
    "MUMBAI", "NAGPUR", "TAXI", "PRIVATE", "HIGHWAY", "POLICE", "SPINNY",
    "REDMIK20PRO", "AITRIPLECAMERA", "REDMI", "K20PRO", "TRIPLECAMERA", "JPG",
    "OOO", "DOO", "INDIA", "BHARAT", "COMMERCIAL", "PASSENGER", "VEHICLE",
    "TRANSPORT", "DL", "GJ", "KA", "KSAIDEEPWHEELS"
]

# Updated license plate validation patterns (relaxed to allow spaces)
PLATE_VALIDATION_PATTERNS: List[str] = [
    r'^MH\d{2}[A-Z]{2}\d{4}$',          # Standard: MH12MB8677
    r'^MH\s?\d{2}\s?[A-Z]{2}\s?\d{4}$', # Allow spaces: MH 12 MB 8677
    r'^MH\d{2}\d{4}$',                   # Alternative: MH121234
    r'^MH\d{3,5}$',                      # Older: MH1201
    r'^MH\d{2}[A-Z]{1,2}\d{1,4}$'       # Relaxed: Allow for slight variations
]

# --- Image Utilities ---

def crop_image(image_path: str, bbox: List[float]) -> np.ndarray:
    """
    Crop an image using provided bounding box coordinates.
    
    Args:
        image_path (str): Path to the image file.
        bbox (List[float]): Bounding box coordinates [xmin, ymin, xmax, ymax].
        
    Returns:
        np.ndarray: Cropped image as a NumPy array.
        
    Raises:
        ValueError: If the image cannot be loaded or the cropped image is empty.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image at {image_path}")
    xmin, ymin, xmax, ymax = map(int, bbox)
    cropped = image[ymin:ymax, xmin:xmax]
    if cropped.size == 0:
        raise ValueError("Cropped image is empty")
    return cropped

def preprocess_image(img: np.ndarray, method: int = 1) -> np.ndarray:
    """
    Apply preprocessing to enhance plate image for OCR with multiple methods.
    
    Args:
        img (np.ndarray): Input image as a NumPy array.
        method (int): Preprocessing method (1-5):
            1: CLAHE + Adaptive Thresholding
            2: Blur + Otsu's thresholding
            3: Contrast adjustment + Denoising
            4: Histogram equalization + Sharpening
            5: Bilateral filter + Adaptive Thresholding
            
    Returns:
        np.ndarray: Preprocessed image as a NumPy array.
    """
    if len(img.shape) > 2 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    if method == 1:
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        return cv2.morphologyEx(dilated, cv2.MORPH_OPEN, kernel)
    
    elif method == 2:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    elif method == 3:
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        return denoised
    
    elif method == 4:
        equalized = cv2.equalizeHist(gray)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(equalized, -1, kernel)
        return sharpened
    
    else:  # method 5
        bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
        thresh = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return thresh

def try_additional_preprocessing(gray_image: np.ndarray) -> List[np.ndarray]:
    """
    Apply additional preprocessing techniques to improve OCR.
    
    Args:
        gray_image (np.ndarray): Grayscale input image as a NumPy array.
        
    Returns:
        List[np.ndarray]: List of preprocessed images.
    """
    return [
        cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5),
        (gray_image - gray_image.min()) * (255.0 / (gray_image.max() - gray_image.min())),
        cv2.Laplacian(gray_image, cv2.CV_8U, ksize=3)
    ]

def correct_rotation(image: np.ndarray) -> np.ndarray:
    """
    Detect and correct rotation in the image using Hough transform.
    
    Args:
        image (np.ndarray): Input image as a NumPy array.
        
    Returns:
        np.ndarray: Rotated image as a NumPy array.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
    
    if lines is not None:
        for rho, theta in lines[0]:
            angle = (theta * 180 / np.pi) - 90
            if abs(angle) > 5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h))
                logger.debug(f"Applied rotation correction: {angle:.2f} degrees")
                return rotated
    return image

# --- OCR Wrapper Functions ---

def extract_paddle_text(result: Any, debug_prefix: Optional[str] = None) -> Tuple[str, float]:
    """
    Extract text and confidence from PaddleOCR result, merging regions intelligently.
    
    Args:
        result (Any): PaddleOCR output.
        debug_prefix (Optional[str]): If provided, log debug info with this prefix.
        
    Returns:
        Tuple[str, float]: Extracted text and confidence score.
    """
    texts: List[str] = []
    confidences: List[float] = []
    
    try:
        if not result or not isinstance(result, list) or len(result) == 0:
            if debug_prefix:
                logger.debug(f"OCR regions ({debug_prefix}): Empty or invalid result: {result}")
            return "", 0.0
        
        # Log raw result for debugging
        if debug_prefix:
            logger.debug(f"Raw PaddleOCR result ({debug_prefix}): {result}")
        
        # Flatten the result if it's nested (PaddleOCR output varies by version)
        regions: List[Dict[str, Any]] = []
        # Check if result is a nested list (older PaddleOCR versions)
        if isinstance(result[0], list):
            for line in result:
                if not isinstance(line, (list, tuple)):
                    if debug_prefix:
                        logger.debug(f"Skipping invalid line in result ({debug_prefix}): {line}")
                    continue
                for item in line:
                    if not isinstance(item, (list, tuple)):
                        if debug_prefix:
                            logger.debug(f"Skipping non-list/tuple item ({debug_prefix}): {item}")
                        continue
                    if len(item) < 2:
                        if debug_prefix:
                            logger.debug(f"Skipping item with insufficient length ({debug_prefix}): {item}")
                        continue
                    bbox = item[0]
                    text_conf = item[1]
                    if not isinstance(bbox, (list, tuple)) or len(bbox) < 4:
                        if debug_prefix:
                            logger.debug(f"Skipping malformed bbox ({debug_prefix}): {bbox}")
                        continue
                    if not isinstance(text_conf, (list, tuple)) or len(text_conf) < 2:
                        if debug_prefix:
                            logger.debug(f"Skipping malformed text_conf ({debug_prefix}): {text_conf}")
                        continue
                    text, conf = text_conf
                    if not all(isinstance(point, (list, tuple)) and len(point) >= 2 for point in bbox):
                        if debug_prefix:
                            logger.debug(f"Skipping invalid bbox points ({debug_prefix}): {bbox}")
                        continue
                    y_center = (bbox[0][1] + bbox[2][1]) / 2
                    regions.append({"text": text, "conf": float(conf), "y": y_center})
        else:
            # Handle flat list structure (newer PaddleOCR versions)
            for item in result:
                if not isinstance(item, (list, tuple)):
                    if debug_prefix:
                        logger.debug(f"Skipping non-list/tuple item ({debug_prefix}): {item}")
                    continue
                if len(item) < 2:
                    if debug_prefix:
                        logger.debug(f"Skipping item with insufficient length ({debug_prefix}): {item}")
                    continue
                bbox = item[0]
                text_conf = item[1]
                if not isinstance(bbox, (list, tuple)) or len(bbox) < 4:
                    if debug_prefix:
                        logger.debug(f"Skipping malformed bbox ({debug_prefix}): {bbox}")
                    continue
                if not isinstance(text_conf, (list, tuple)) or len(text_conf) < 2:
                    if debug_prefix:
                        logger.debug(f"Skipping malformed text_conf ({debug_prefix}): {text_conf}")
                    continue
                text, conf = text_conf
                if not all(isinstance(point, (list, tuple)) and len(point) >= 2 for point in bbox):
                    if debug_prefix:
                        logger.debug(f"Skipping invalid bbox points ({debug_prefix}): {bbox}")
                    continue
                y_center = (bbox[0][1] + bbox[2][1]) / 2
                regions.append({"text": text, "conf": float(conf), "y": y_center})
        
        if not regions:
            if debug_prefix:
                logger.debug(f"OCR regions ({debug_prefix}): No valid regions detected")
            return "", 0.0
        
        # Sort regions by y-coordinate to group lines
        regions.sort(key=lambda x: x["y"])
        
        # Group regions into lines based on y-coordinate proximity
        lines: List[List[Dict[str, Any]]] = []
        current_line: List[Dict[str, Any]] = []
        for i, region in enumerate(regions):
            if i == 0:
                current_line.append(region)
                continue
            if abs(region["y"] - regions[i-1]["y"]) < 10:
                current_line.append(region)
            else:
                lines.append(current_line)
                current_line = [region]
        if current_line:
            lines.append(current_line)
        
        # Process each line
        for line in lines:
            line_text: List[str] = []
            line_conf: List[float] = []
            # Sort within line: prioritize regions starting with 'MH'
            line.sort(key=lambda x: (x["text"].startswith('MH'), x["y"]))
            for region in line:
                text = region["text"]
                conf = region["conf"]
                if text.startswith('MH') or re.match(r'^M[H0O]', text):
                    line_text.insert(0, text)
                    line_conf.insert(0, conf)
                else:
                    line_text.append(text)
                    line_conf.append(conf)
            merged = "".join(line_text)
            avg_conf = sum(line_conf) / len(line_conf) if line_conf else 0.0
            texts.append(merged)
            confidences.append(avg_conf)
        
        merged_text = " ".join(texts)
        confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        if debug_prefix:
            logger.debug(f"OCR regions ({debug_prefix}): {texts}, Merged: '{merged_text}', Conf: {confidence:.2f}")
        
        return merged_text, confidence
    except Exception as e:
        if debug_prefix:
            logger.error(f"Error parsing PaddleOCR output ({debug_prefix}): {str(e)}", exc_info=True)
        return "", 0.0

def process_with_paddle_ocr(
    image: np.ndarray, 
    debug_prefix: Optional[str] = None
) -> Tuple[str, float, np.ndarray]:
    """
    Process image with PaddleOCR with optional debugging.
    
    Args:
        image (np.ndarray): Input image as a NumPy array.
        debug_prefix (Optional[str]): If provided, save debug images with this prefix.
        
    Returns:
        Tuple[str, float, np.ndarray]: Extracted text, confidence score, and processed image.
    """
    if debug_prefix:
        os.makedirs("debug", exist_ok=True)
        debug_path = f"debug/{debug_prefix}_input.jpg"
        cv2.imwrite(debug_path, image)
        logger.debug(f"Saved PaddleOCR input image to {debug_path}")
    
    try:
        result = paddle_ocr.ocr(image, cls=True, det=True, rec=True)
        if debug_prefix:
            logger.debug(f"PaddleOCR raw output ({debug_prefix}): {result}")
        text, confidence = extract_paddle_text(result, debug_prefix)
        return text, confidence, image
    except Exception as e:
        if debug_prefix:
            logger.error(f"PaddleOCR processing failed ({debug_prefix}): {str(e)}", exc_info=True)
        return "", 0.0, image

def process_with_tesseract(image: np.ndarray, debug_prefix: Optional[str] = None) -> Tuple[str, float]:
    """
    Fallback OCR using Tesseract if PaddleOCR fails.
    
    Args:
        image (np.ndarray): Input image as a NumPy array.
        debug_prefix (Optional[str]): If provided, log debug info with this prefix.
        
    Returns:
        Tuple[str, float]: Extracted text and confidence score.
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract unavailable, skipping fallback OCR")
        return "", 0.0
    
    try:
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = pytesseract.image_to_string(image, config=custom_config).strip()
        confidence = 0.7  # Default confidence for Tesseract
        if debug_prefix:
            logger.debug(f"Tesseract OCR ({debug_prefix}): '{text}' (conf: {confidence:.2f})")
        return text, confidence
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {str(e)}", exc_info=True)
        return "", 0.0

# --- Text Cleanup Functions ---

def correct_characters(plate_text: str, debug: bool = False) -> str:
    """
    Apply context-aware character corrections for MH01OE1234 or MH1201 formats.
    
    Args:
        plate_text (str): OCR-detected text.
        debug (bool): Enable debug logging.
        
    Returns:
        str: Corrected text.
    """
    if not plate_text:
        if debug:
            logger.debug("Input is empty")
        return ""
    
    if debug:
        logger.debug(f"Correcting characters: '{plate_text}'")
    
    plate_text = plate_text.upper()
    
    if re.match(r'^MH\d{2}[A-Z]{2}\d{4}$', plate_text):
        if debug:
            logger.debug(f"Direct valid match: '{plate_text}'")
        return plate_text
    
    mh_match = re.search(r'MH\d{2}[A-Z]{1,2}\d{1,4}', plate_text)
    if mh_match:
        if debug:
            logger.debug(f"Extracted match: '{mh_match.group(0)}'")
        return mh_match.group(0)
    
    if len(plate_text) >= 8:
        match = re.match(r'^([A-Z0-9]{2})([0-9O]{2})([A-Z0-9]{1,2})([0-9OIlBSZGTE]{0,4})$', plate_text)
        if match:
            state, district, series, number = match.groups()
            if debug:
                logger.debug(f"Matched groups: state='{state}', district='{district}', series='{series}', number='{number}'")
            
            corrected_state = ''.join('O' if c == '0' else c for c in state)
            if corrected_state != 'MH':
                if debug:
                    logger.debug("Rejected: Invalid state code")
                return ""
            
            corrected_district = ''.join('0' if c == 'O' else c for c in district)
            if len(corrected_district) != 2 or not corrected_district.isdigit():
                if debug:
                    logger.debug("Rejected: Invalid district")
                return ""
            
            corrected_series = ''.join('O' if c == '0' else c for c in series if c.isalpha() or c == '0')
            if not (1 <= len(corrected_series) <= 2) or not corrected_series.isalpha():
                if debug:
                    logger.debug("Rejected: Invalid series")
                return ""
            
            corrected_number = ''.join(
                '0' if c == 'O' else '1' if c in ['I', 'l'] else '8' if c in ['B', 'E'] else
                '5' if c == 'S' else '2' if c == 'Z' else '6' if c in ['G'] else '7' if c == 'T' else c
                for c in number
            )
            if len(corrected_number) != 4 or not corrected_number.isdigit():
                if debug:
                    logger.debug("Rejected: Invalid number")
                return ""
            
            result = corrected_state + corrected_district + corrected_series + corrected_number
            if debug:
                logger.debug(f"Corrected result: '{result}'")
            return result
    
    if len(plate_text) >= 5:
        match = re.match(r'^([A-Z0-9]{2})([0-9O]{3,5})$', plate_text)
        if match:
            state, number = match.groups()
            corrected_state = ''.join('O' if c == '0' else c for c in state)
            if corrected_state != 'MH':
                if debug:
                    logger.debug("Rejected: Invalid state code (older)")
                return ""
            corrected_number = ''.join('0' if c == 'O' else c for c in number)
            if not (3 <= len(corrected_number) <= 5) or not corrected_number.isdigit():
                if debug:
                    logger.debug("Rejected: Invalid number (older)")
                return ""
            result = corrected_state + corrected_number
            if debug:
                logger.debug(f"Older format result: '{result}'")
            return result
    
    if debug:
        logger.debug("No valid plate found")
    return ""

def remove_ind(text: str) -> Tuple[str, bool]:
    """
    Remove 'IND' from text using multiple patterns.
    
    Args:
        text (str): Input text.
        
    Returns:
        Tuple[str, bool]: Cleaned text and a flag indicating if 'IND' was found.
    """
    if not text:
        return "", False
        
    ind_found = False
    
    for pattern in IND_PATTERNS:
        if re.search(pattern, text):
            text = re.sub(pattern, r'\1\2', text)
            ind_found = True
    
    if "IND" in text:
        ind_found = True
        text = text.replace("IND", "")
    
    return text, ind_found

def clean_plate_text(text: str, debug: bool = False) -> str:
    """
    Clean license plate text by removing unwanted patterns and applying corrections.
    
    Args:
        text (str): Input text.
        debug (bool): Enable debug logging.
        
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""
    
    if debug:
        logger.debug(f"Cleaning text: '{text}'")
    
    # Remove spaces, dots, and other unwanted characters, but preserve core text
    text = re.sub(r'[\.\s]', '', text).upper()
    if debug:
        logger.debug(f"After removing dots/spaces: '{text}'")
    
    # Remove long numbers that are unlikely to be part of the plate
    text = re.sub(r'\d{7,}', '', text)
    if debug:
        logger.debug(f"After removing long numbers: '{text}'")
    
    # Remove unwanted text
    for unwanted in UNWANTED_TEXT:
        text = text.replace(unwanted, "")
    if debug:
        logger.debug(f"After removing unwanted text: '{text}'")
    
    # Remove 'IND'
    text, ind_found = remove_ind(text)
    if debug and ind_found:
        logger.debug(f"After removing IND: '{text}'")
    
    # Apply character corrections
    text = correct_characters(text, debug)
    if debug:
        logger.debug(f"Final cleaned text: '{text}'")
    
    return text

# --- Pattern Matching and Validation Functions ---

def extract_plate_number(text: str, debug: bool = False) -> str:
    """
    Extract the actual license plate number from OCR text.
    
    Args:
        text (str): Input text.
        debug (bool): Enable debug logging.
        
    Returns:
        str: Extracted license plate number.
    """
    if not text:
        return ""
    
    if debug:
        logger.debug(f"Extracting plate number from: '{text}'")
    
    text = clean_plate_text(text, debug)
    
    # Relaxed patterns to allow for slight variations
    patterns: List[str] = [
        r'(MH\d{2}[A-Z]{2}\d{4})',          # Standard: MH12MB8677
        r'(MH\s?\d{2}\s?[A-Z]{2}\s?\d{4})', # Allow spaces: MH 12 MB 8677
        r'(MH\d{2}\d{4})',                   # Alternative: MH121234
        r'(MH\d{3,5})',                      # Older: MH1201
        r'(MH\d{2}[A-Z]{1,2}\d{1,4})',      # Relaxed: Allow slight variations
        r'.*(MH\d{2}[A-Z]{1,2}\d{1,4}).*'   # Extract MH plate from noise
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            plate = match.group(1)
            # Remove any spaces from the matched plate
            plate = plate.replace(" ", "")
            if validate_license_plate(plate):
                if debug:
                    logger.debug(f"Extracted valid plate: '{plate}'")
                return plate
    
    # Fallback: If text starts with 'MH', take up to 10 characters
    if text.startswith('MH'):
        plate = text[:min(10, len(text))]
        plate = plate.replace(" ", "")  # Remove spaces
        if validate_license_plate(plate):
            if debug:
                logger.debug(f"Fallback valid plate: '{plate}'")
            return plate
    
    if debug:
        logger.debug("No valid plate extracted")
    return ""

def validate_license_plate(text: str) -> bool:
    """
    Validate if text matches MH license plate formats.
    
    Args:
        text (str): License plate text to validate.
        
    Returns:
        bool: True if the plate format is valid, False otherwise.
    """
    if not text or len(text) < 5 or len(text) > 10:
        return False
    
    for pattern in PLATE_VALIDATION_PATTERNS:
        if re.match(pattern, text):
            return True
    
    return False

# --- High-Level Pipeline Functions ---

def ocr_plate(cropped_image: np.ndarray, debug: bool = False) -> str:
    """
    Extract and validate plate text with priority to the original method.
    
    Args:
        cropped_image (np.ndarray): Cropped image of the license plate as a NumPy array.
        debug (bool): Enable debug output.
        
    Returns:
        str: Extracted plate text.
    """
    if cropped_image is None or cropped_image.size == 0:
        if debug:
            logger.warning("Input image is empty or None")
        return ""
    
    best_results: List[Dict[str, Any]] = []
    if debug:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/cropped_original.jpg", cropped_image)
        logger.debug("Saved cropped original image to debug/cropped_original.jpg")
    
    # Correct rotation
    corrected_image = correct_rotation(cropped_image)
    if debug:
        cv2.imwrite("debug/rotated.jpg", corrected_image)
        logger.debug("Saved rotated image to debug/rotated.jpg")
    
    # Prioritize the original method
    text, conf, _ = process_with_paddle_ocr(corrected_image, "original" if debug else None)
    if text:
        plate = extract_plate_number(text, debug)
        plate, has_ind = remove_ind(plate)
        is_valid = validate_license_plate(plate)
        score = conf * (0.9 if has_ind else 1.0) * (10.0 if is_valid else 0.5)
        best_results.append({"plate": plate, "conf": conf, "score": score, "valid": is_valid, "source": "PaddleOCR"})
        
        if is_valid and conf > 0.9:  # Early stopping for high-confidence valid results
            if debug:
                logger.info(f"Original method produced valid plate: '{plate}' with high confidence ({conf:.2f}), stopping further processing")
            return plate
    
    # If original method fails, proceed with other methods
    methods = [
        (preprocess_image(corrected_image, 1), "method1"),
        (preprocess_image(corrected_image, 2), "method2"),
        (preprocess_image(corrected_image, 3), "method3"),
        (preprocess_image(cropped_image, 4), "method4"),
        (preprocess_image(cropped_image, 5), "method5")
    ]
    gray = cv2.cvtColor(corrected_image, cv2.COLOR_BGR2GRAY) if len(cropped_image.shape) > 2 else cropped_image
    methods.extend([(img, f"additional{i+1}") for i, img in enumerate(try_additional_preprocessing(gray))])
    
    # Try other PaddleOCR methods
    for img, name in methods:
        if debug:
            debug_path = f"debug/{name}.jpg"
            cv2.imwrite(debug_path, img)
            logger.debug(f"Saved preprocessed image to {debug_path}")
        text, conf, _ = process_with_paddle_ocr(img, name if debug else None)
        if text:
            plate = extract_plate_number(text, debug)
            plate, has_ind = remove_ind(plate)
            is_valid = validate_license_plate(plate)
            score = conf * (0.9 if has_ind else 1.0) * (10.0 if is_valid else 0.5)
            best_results.append({"plate": plate, "conf": conf, "score": score, "valid": is_valid, "source": "PaddleOCR"})
            
            if is_valid and conf > 0.9:  # Early stopping
                if debug:
                    logger.info(f"Method {name} produced valid plate: '{plate}' with high confidence ({conf:.2f}), stopping further processing")
                return plate
    
    # Fallback to Tesseract if no valid results
    if not any(r["valid"] for r in best_results):
        for img, name in methods:
            text, conf = process_with_tesseract(img, name if debug else None)
            if text:
                plate = extract_plate_number(text, debug)
                plate, has_ind = remove_ind(plate)
                is_valid = validate_license_plate(plate)
                score = conf * (0.9 if has_ind else 1.0) * (10.0 if is_valid else 0.5) * 0.8
                best_results.append({"plate": plate, "conf": conf, "score": score, "valid": is_valid, "source": "Tesseract"})
                
                if is_valid and conf > 0.9:  # Early stopping
                    if debug:
                        logger.info(f"Tesseract method {name} produced valid plate: '{plate}' with high confidence ({conf:.2f}), stopping further processing")
                    return plate
    
    if not best_results:
        return ""
    
    best_results.sort(key=lambda x: x["score"], reverse=True)
    valid = [r for r in best_results if r["valid"]]
    result = valid[0]["plate"] if valid else ""
    if debug:
        logger.debug(f"Final plate: '{result}', Valid results: {len(valid)}, All results: {best_results}")
    return result

def get_plate_details(cropped_image: np.ndarray, debug: bool = False, apply_rotation: bool = True) -> Dict[str, Any]:
    """
    Get detailed plate information with priority to the original method.
    
    Args:
        cropped_image (np.ndarray): Cropped image of the license plate as a NumPy array.
        debug (bool): Enable debug output.
        apply_rotation (bool): Whether to apply rotation correction (default: True).
        
    Returns:
        Dict[str, Any]: Dictionary with plate text and metadata.
    """
    if cropped_image is None or cropped_image.size == 0:
        if debug:
            logger.warning("Input image is empty or None")
        return {
            "plate_text": "",
            "raw_text": "",
            "confidence": 0.0,
            "valid": False,
            "source": "None"
        }
    
    best_results: List[Dict[str, Any]] = []
    if debug:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/cropped_original.jpg", cropped_image)
        logger.debug("Saved cropped original image to debug/cropped_original.jpg")
    
    # Correct rotation if requested
    if apply_rotation:
        corrected_image = correct_rotation(cropped_image)
        if debug:
            cv2.imwrite("debug/rotated.jpg", corrected_image)
            logger.debug("Saved rotated image to debug/rotated.jpg")
    else:
        corrected_image = cropped_image
        if debug:
            logger.debug("Skipped rotation correction as per request")
    
    # Prioritize the original method
    raw, conf, _ = process_with_paddle_ocr(corrected_image, "original" if debug else None)
    if raw:
        plate = extract_plate_number(raw, debug)
        plate, has_ind = remove_ind(plate)
        is_valid = validate_license_plate(plate)
        score = conf * (0.9 if has_ind else 1.0) * (10.0 if is_valid else 0.5)
        best_results.append({
            "plate": plate,
            "raw": raw,
            "conf": conf,
            "score": score,
            "valid": is_valid,
            "source": "PaddleOCR"
        })
        
        if is_valid and conf > 0.9:  # Early stopping for high-confidence valid results
            if debug:
                logger.info(f"Original method produced valid plate: '{plate}' with high confidence ({conf:.2f}), stopping further processing")
            return {
                "plate_text": plate,
                "raw_text": raw,
                "confidence": conf,
                "valid": is_valid,
                "source": "PaddleOCR"
            }
    
    # If original method fails, proceed with other methods
    methods = [
        (preprocess_image(corrected_image, 1), "method1"),  # CLAHE + Adaptive Thresholding
        (preprocess_image(corrected_image, 3), "method3"),  # Contrast + Denoising
        (preprocess_image(corrected_image, 4), "method4"),  # Histogram Equalization + Sharpening
    ]
    gray = cv2.cvtColor(corrected_image, cv2.COLOR_BGR2GRAY) if len(cropped_image.shape) > 2 else cropped_image
    additional_methods = [(img, f"additional{i+1}") for i, img in enumerate(try_additional_preprocessing(gray))]
    methods.extend(additional_methods[:2])  # Limit to top 2 additional methods for performance
    
    # Try other PaddleOCR methods
    for img, name in methods:
        if debug:
            debug_path = f"debug/{name}.jpg"
            cv2.imwrite(debug_path, img)
            logger.debug(f"Saved preprocessed image to {debug_path}")
        raw, conf, _ = process_with_paddle_ocr(img, name if debug else None)
        if raw:
            plate = extract_plate_number(raw, debug)
            plate, has_ind = remove_ind(plate)
            is_valid = validate_license_plate(plate)
            score = conf * (0.9 if has_ind else 1.0) * (10.0 if is_valid else 0.5)
            best_results.append({
                "plate": plate,
                "raw": raw,
                "conf": conf,
                "score": score,
                "valid": is_valid,
                "source": "PaddleOCR"
            })
            
            if is_valid and conf > 0.9:  # Early stopping
                if debug:
                    logger.info(f"Method {name} produced valid plate: '{plate}' with high confidence ({conf:.2f}), stopping further processing")
                return {
                    "plate_text": plate,
                    "raw_text": raw,
                    "confidence": conf,
                    "valid": is_valid,
                    "source": "PaddleOCR"
                }
    
    # Fallback to Tesseract if no valid results
    if not any(r["valid"] for r in best_results):
        for img, name in methods:
            raw, conf = process_with_tesseract(img, name if debug else None)
            if raw:
                plate = extract_plate_number(raw, debug)
                plate, has_ind = remove_ind(plate)
                is_valid = validate_license_plate(plate)
                score = conf * (0.9 if has_ind else 1.0) * (10.0 if is_valid else 0.5) * 0.8
                best_results.append({
                    "plate": plate,
                    "raw": raw,
                    "conf": conf,
                    "score": score,
                    "valid": is_valid,
                    "source": "Tesseract"
                })
                
                if is_valid and conf > 0.9:  # Early stopping
                    if debug:
                        logger.info(f"Tesseract method {name} produced valid plate: '{plate}' with high confidence ({conf:.2f}), stopping further processing")
                    return {
                        "plate_text": plate,
                        "raw_text": raw,
                        "confidence": conf,
                        "valid": is_valid,
                        "source": "Tesseract"
                    }
    
    if not best_results:
        return {
            "plate_text": "",
            "raw_text": "",
            "confidence": 0.0,
            "valid": False,
            "source": "None"
        }
    
    best_results.sort(key=lambda x: x["score"], reverse=True)
    valid = [r for r in best_results if r["valid"]]
    result = valid[0] if valid else best_results[0]
    if debug:
        logger.debug(f"Selected result: plate='{result['plate']}', valid={result['valid']}, conf={result['conf']:.2f}, source={result['source']}")
    return {
        "plate_text": result["plate"],
        "raw_text": result["raw"],
        "confidence": result["conf"],
        "valid": result["valid"],
        "source": result["source"]
    }

def batch_process_plates(image_paths: List[str], output_dir: str = None, debug: bool = False) -> List[Dict[str, Any]]:
    """
    Process multiple images and save results.
    
    Args:
        image_paths (List[str]): List of image paths.
        output_dir (str, optional): Directory to save output images.
        debug (bool): Enable debug output.
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries with plate details.
    """
    results: List[Dict[str, Any]] = []
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Created output directory: {output_dir}")
    
    for idx, path in enumerate(image_paths):
        try:
            image = cv2.imread(path)
            if image is None:
                logger.error(f"Error loading {path}")
                continue
            logger.info(f"Processing {idx+1}/{len(image_paths)}: {os.path.basename(path)}")
            details = get_plate_details(image, debug, apply_rotation=True)
            details["filename"] = os.path.basename(path)
            results.append(details)
            
            if output_dir and details["plate_text"]:
                output_path = os.path.join(output_dir, f"{details['plate_text']}_{details['filename']}")
                result_img = image.copy()
                cv2.putText(result_img, details["plate_text"], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(result_img, f"Raw: {details['raw_text'][:20]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
                cv2.putText(result_img, f"Conf: {details['confidence']:.2f}, Valid: {details['valid']}, Source: {details['source']}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
                cv2.imwrite(output_path, result_img)
                logger.debug(f"Saved annotated image to {output_path}")
        except Exception as e:
            logger.error(f"Error processing {path}: {str(e)}", exc_info=True)
    return results

if __name__ == "__main__":
    images = ["path/to/image1.jpg", "path/to/image2.jpg"]
    results = batch_process_plates(images, "output", debug=True)
    for r in results:
        logger.info(f"File: {r['filename']}, Plate: {r['plate_text']}, Valid: {r['valid']}, Source: {r['source']}")