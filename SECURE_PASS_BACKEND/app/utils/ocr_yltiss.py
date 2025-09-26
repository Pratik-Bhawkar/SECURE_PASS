import cv2
import os
import re
import numpy as np
from paddleocr import PaddleOCR
from typing import List, Dict, Tuple, Union, Optional, Any

# Initialize PaddleOCR model
paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en")

# Patterns and constants for license plate processing
STATE_CODES = ['MH']  # Restrict to MH only

# Common OCR misrecognitions to correct (excluding 0/O as handled contextually)
CHAR_CORRECTIONS = {
    '$': 'S',
    'I': '1',
    'B': '8',
    'D': '0',
    'Q': '0',
    'Z': '2',
    'S': '5',
    'l': '1'
}

# IND removal patterns tailored for MH01OE1234 and MH1201 formats
IND_PATTERNS = [
    r'(MH\d{2})IND([A-Z]{2}\d{4})',
    r'(MH\d{2}[A-Z]{2})IND(\d{4})',
    r'(MH)IND(\d{2}[A-Z]{2}\d{4})',
    r'(MH\d{2})I\s*N\s*D([A-Z]{2}\d{4})',
    r'(MH)IND(\d{3,5})'
]

# Unwanted text in license plates
UNWANTED_TEXT = [
    "SCO", "OKULNAGAR", "ONDA", "METRO", "CO0DN", "GARDEN", "PUNE",
    "MUMBAI", "NAGPUR", "TAXI", "PRIVATE", "HIGHWAY", "POLICE"
]

# License plate validation patterns
PLATE_VALIDATION_PATTERNS = [
    r'^MH\d{2}[A-Z]{2}\d{4}$',  # Standard: MH01OE1234
    r'^MH\d{3,5}$',             # Older: MH1201
]

# --- Image Utilities ---

def crop_image(image_path: str, bbox: List[float]) -> np.ndarray:
    """
    Crop an image using provided bounding box coordinates.
    
    Args:
        image_path: Path to the image file
        bbox: Bounding box coordinates [xmin, ymin, xmax, ymax]
        
    Returns:
        Cropped image as numpy ndarray
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image at {image_path}")
    xmin, ymin, xmax, ymax = map(int, bbox)
    return image[ymin:ymax, xmin:xmax]

def preprocess_image(img: np.ndarray, method: int = 1) -> np.ndarray:
    """
    Apply preprocessing to enhance plate image for OCR with multiple methods.
    
    Args:
        img: Input image as numpy ndarray
        method: Preprocessing method (1-2)
            1: CLAHE + Adaptive Thresholding
            2: Blur + Otsu's thresholding
            
    Returns:
        Preprocessed image as numpy ndarray
    """
    if len(img.shape) > 2 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
        
    if method == 1:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        return cv2.morphologyEx(dilated, cv2.MORPH_OPEN, kernel)
            
    else:  # method 2
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

def try_additional_preprocessing(gray_image: np.ndarray) -> List[np.ndarray]:
    """
    Apply additional preprocessing techniques to improve OCR.
    
    Args:
        gray_image: Grayscale input image
        
    Returns:
        List of preprocessed images
    """
    return [
        cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5)
    ]

# --- OCR Wrapper Functions ---

def extract_paddle_text(result: Any, debug_prefix: Optional[str] = None) -> Tuple[str, float]:
    """
    Extract text and confidence from PaddleOCR result, merging regions.
    
    Args:
        result: PaddleOCR output
        debug_prefix: If provided, log debug info
        
    Returns:
        Tuple of (extracted text, confidence score)
    """
    texts = []
    confidences = []
    
    try:
        if not result:
            return "", 0.0
            
        for line in result:
            if not line:
                continue
            for item in line:
                if isinstance(item, (list, tuple)) and len(item) > 1:
                    if isinstance(item[1], tuple) and len(item[1]) > 0:
                        text = item[1][0]
                        conf = float(item[1][1])
                        texts.append(text)
                        confidences.append(conf)
                    elif isinstance(item[1], str):
                        texts.append(item[1])
        
        if not texts:
            return "", 0.0
        
        if debug_prefix:
            print(f"OCR regions ({debug_prefix}): {texts}")
        
        # Merge texts, prioritizing MH at start
        merged_text = ""
        mh_index = -1
        for i, text in enumerate(texts):
            if text.startswith('MH') or re.match(r'^M[H0O]', text):
                mh_index = i
                break
        if mh_index >= 0:
            merged_text = texts[mh_index]
            remaining = texts[:mh_index] + texts[mh_index + 1:]
            merged_text += " " + " ".join(remaining)
        else:
            merged_text = " ".join(texts)
            
        confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return merged_text, confidence
    except Exception as e:
        print(f"Error parsing PaddleOCR output: {e}")
        return "", 0.0

def process_with_paddle_ocr(
    image: np.ndarray, 
    debug_prefix: Optional[str] = None
) -> Tuple[str, float, np.ndarray]:
    """
    Process image with PaddleOCR with optional debugging.
    
    Args:
        image: Input image
        debug_prefix: If provided, save debug images with this prefix
        
    Returns:
        Tuple of (text, confidence, processed_image)
    """
    if debug_prefix:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite(f"debug/{debug_prefix}_input.jpg", image)
    
    result = paddle_ocr.ocr(image, cls=True)
    text, confidence = extract_paddle_text(result, debug_prefix)
    
    if debug_prefix:
        print(f"OCR ({debug_prefix}): '{text}' (conf: {confidence:.2f})")
    
    return text, confidence, image

# --- Text Cleanup Functions ---

def correct_characters(plate_text: str, debug: bool = False) -> str:
    """
    Apply context-aware character corrections for MH01OE1234 or MH1201 formats.
    
    Args:
        plate_text: OCR detected text
        debug: Enable debug logging
        
    Returns:
        Corrected text
    """
    if not plate_text:
        if debug:
            print("Input is empty")
        return ""
    
    if debug:
        print(f"Correcting characters: '{plate_text}'")
    
    # Ensure uppercase and clean input
    plate_text = plate_text.upper()
    
    # Direct validation for standard format (MH12MB8677)
    if re.match(r'^MH\d{2}[A-Z]{2}\d{4}$', plate_text):
        if debug:
            print(f"Direct valid match: '{plate_text}'")
        return plate_text
    
    # Apply general corrections (excluding 0/O)
    for wrong, right in CHAR_CORRECTIONS.items():
        if wrong != '0' and wrong != 'O':
            plate_text = plate_text.replace(wrong, right)
    
    # Try extracting valid MH plate
    mh_match = re.search(r'MH\d{2}[A-Z]{2}\d{4}', plate_text)
    if mh_match:
        if debug:
            print(f"Extracted match: '{mh_match.group(0)}'")
        return mh_match.group(0)
    
    # Handle standard format with corrections
    if len(plate_text) >= 8:
        match = re.match(r'^([A-Z0]{2})([0-9O]{2})([A-Z0]{2})([0-9OIlBSZ]{0,4})$', plate_text)
        if match:
            state, district, series, number = match.groups()
            if debug:
                print(f"Matched groups: state='{state}', district='{district}', series='{series}', number='{number}'")
            # Correct state: must be MH, 0 → O
            corrected_state = ''.join('O' if c == '0' else c for c in state)
            if corrected_state != 'MH':
                if debug:
                    print("Rejected: Invalid state code")
                return ""
            # Correct district: must be 2 digits, O → 0
            corrected_district = ''.join('0' if c == 'O' else c for c in district if c.isdigit() or c == 'O')
            if len(corrected_district) != 2 or not corrected_district.isdigit():
                if debug:
                    print("Rejected: Invalid district")
                return ""
            # Correct series: must be 2 letters, 0 → O
            corrected_series = ''.join('O' if c == '0' else c for c in series if c.isalpha() or c == '0')
            if len(corrected_series) != 2 or not corrected_series.isalpha():
                if debug:
                    print("Rejected: Invalid series")
                return ""
            # Correct number: must be 4 digits, O → 0
            corrected_number = ''.join(
                '0' if c == 'O' else '1' if c in ['I', 'l'] else '8' if c == 'B' else
                '5' if c == 'S' else '2' if c == 'Z' else c
                for c in number if c.isdigit() or c in ['O', 'I', 'l', 'B', 'S', 'Z']
            )
            if len(corrected_number) != 4 or not corrected_number.isdigit():
                if debug:
                    print("Rejected: Invalid number")
                return ""
            result = corrected_state + corrected_district + corrected_series + corrected_number
            if debug:
                print(f"Corrected result: '{result}'")
            return result
    
    # Handle older format: MH1201
    if len(plate_text) >= 5:
        match = re.match(r'^([A-Z0]{2})([0-9O]{3,5})$', plate_text)
        if match:
            state, number = match.groups()
            corrected_state = ''.join('O' if c == '0' else c for c in state)
            if corrected_state != 'MH':
                if debug:
                    print("Rejected: Invalid state code (older)")
                return ""
            corrected_number = ''.join('0' if c == 'O' else c for c in number if c.isdigit() or c == 'O')
            if not (3 <= len(corrected_number) <= 5) or not corrected_number.isdigit():
                if debug:
                    print("Rejected: Invalid number (older)")
                return ""
            result = corrected_state + corrected_number
            if debug:
                print(f"Older format result: '{result}'")
            return result
    
    if debug:
        print("No valid plate found")
    return ""

def remove_ind(text: str) -> Tuple[str, bool]:
    """
    Remove 'IND' from text using multiple patterns.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (cleaned text, flag indicating if 'IND' was found)
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
        parts = text.split("IND")
        text = "".join(parts)
    
    return text, ind_found

def clean_plate_text(text: str, debug: bool = False) -> str:
    """
    Clean license plate text by removing unwanted patterns and applying corrections.
    
    Args:
        text: Input text
        debug: Enable debug logging
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    if debug:
        print(f"Cleaning text: '{text}'")
    
    # Remove dots, spaces, and convert to uppercase
    text = re.sub(r'[\s\.]', '', text).upper()
    if debug:
        print(f"After removing dots/spaces: '{text}'")
    
    # Remove long numeric sequences (e.g., phone numbers)
    text = re.sub(r'\d{7,}', '', text)
    if debug:
        print(f"After removing long numbers: '{text}'")
    
    # Remove IND
    text, ind_found = remove_ind(text)
    if debug and ind_found:
        print(f"After removing IND: '{text}'")
    
    # Remove unwanted text
    for unwanted in UNWANTED_TEXT:
        text = text.replace(unwanted, "")
    if debug:
        print(f"After removing unwanted text: '{text}'")
    
    # Apply character corrections
    text = correct_characters(text, debug)
    if debug:
        print(f"Final cleaned text: '{text}'")
    
    return text

# --- Pattern Matching and Validation Functions ---

def extract_plate_number(text: str, debug: bool = False) -> str:
    """
    Extract the actual license plate number from OCR text.
    
    Args:
        text: Input text
        debug: Enable debug logging
        
    Returns:
        Extracted license plate number
    """
    if not text:
        return ""
    
    if debug:
        print(f"Extracting plate number from: '{text}'")
    
    text = clean_plate_text(text, debug)
    
    patterns = [
        r'(MH\d{2}[A-Z]{2}\d{4})',  # Standard: MH01OE1234
        r'(MH\d{3,5})',             # Older: MH1201
        r'.*(MH\d{2}[A-Z]{2}\d{4}).*'  # Extract MH plate from noise
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if debug:
                print(f"Extracted plate: '{match.group(1)}'")
            return match.group(1)
    
    if text.startswith('MH'):
        plate = text[:min(10, len(text))]
        if re.match(r'^MH\d{2}[A-Z]{2}\d{4}$|^MH\d{3,5}$', plate):
            if debug:
                print(f"Fallback plate: '{plate}'")
            return plate
    
    if debug:
        print("No plate extracted")
    return ""

def validate_license_plate(text: str) -> bool:
    """
    Validate if text matches MH license plate formats.
    
    Args:
        text: License plate text to validate
        
    Returns:
        Boolean indicating if the plate format is valid
    """
    if not text or len(text) < 5 or len(text) > 10 or "IND" in text:
        return False
    
    for pattern in PLATE_VALIDATION_PATTERNS:
        if re.match(pattern, text):
            return True
    
    return False

# --- High-Level Pipeline Functions ---

def ocr_plate(cropped_image: np.ndarray, debug: bool = False) -> str:
    """
    Extract and validate plate text using multiple preprocessing methods.
    
    Args:
        cropped_image: Cropped image of the license plate
        debug: Enable debug output
        
    Returns:
        Extracted plate text
    """
    best_results = []
    if debug:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/cropped_original.jpg", cropped_image)
    
    methods = [(cropped_image, "original")] + [(preprocess_image(cropped_image, i), f"method{i}") for i in range(1, 3)]
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY) if len(cropped_image.shape) > 2 else cropped_image
    methods.extend([(img, f"additional{i+1}") for i, img in enumerate(try_additional_preprocessing(gray))])
    
    for img, name in methods:
        if debug:
            cv2.imwrite(f"debug/{name}.jpg", img)
        text, conf, _ = process_with_paddle_ocr(img, name if debug else None)
        if text:
            plate = extract_plate_number(text, debug)
            plate, has_ind = remove_ind(plate)
            is_valid = validate_license_plate(plate)
            score = conf * (0.8 if has_ind else 1.0) * (10.0 if is_valid else 0.7)  # Boost valid plates
            best_results.append({"plate": plate, "conf": conf, "score": score, "valid": is_valid})
    
    best_results.sort(key=lambda x: x["score"], reverse=True)
    valid = [r for r in best_results if r["valid"]]
    result = valid[0]["plate"] if valid else ""
    if debug:
        print(f"Final plate: '{result}', Valid results: {len(valid)}")
    return result

def get_plate_details(cropped_image: np.ndarray, debug: bool = False) -> Dict[str, Any]:
    """
    Get detailed plate information from a cropped image.
    
    Args:
        cropped_image: Cropped image of the license plate
        debug: Enable debug output
        
    Returns:
        Dictionary with plate text and metadata
    """
    best_results = []
    if debug:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/cropped_original.jpg", cropped_image)
    
    methods = [(cropped_image, "original")] + [(preprocess_image(cropped_image, i), f"method{i}") for i in range(1, 3)]
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY) if len(cropped_image.shape) > 2 else cropped_image
    methods.extend([(img, f"additional{i+1}") for i, img in enumerate(try_additional_preprocessing(gray))])
    
    for img, name in methods:
        if debug:
            cv2.imwrite(f"debug/{name}.jpg", img)
        raw, conf, _ = process_with_paddle_ocr(img, name if debug else None)
        if raw:
            plate = extract_plate_number(raw, debug)
            plate, has_ind = remove_ind(plate)
            is_valid = validate_license_plate(plate)
            score = conf * (0.8 if has_ind else 1.0) * (10.0 if is_valid else 0.7)  # Boost valid plates
            best_results.append({"plate": plate, "raw": raw, "conf": conf, "score": score, "valid": is_valid})
    
    best_results.sort(key=lambda x: x["score"], reverse=True)
    valid = [r for r in best_results if r["valid"]]
    result = valid[0] if valid else best_results[0] if best_results else {"plate": "", "raw": "", "conf": 0.0, "valid": False}
    if debug:
        print(f"Selected result: plate='{result['plate']}', valid={result['valid']}, conf={result['conf']}")
    return {
        "plate_text": result["plate"],
        "raw_text": result["raw"],
        "confidence": result["conf"],
        "valid": result["valid"]
    }

def batch_process_plates(image_paths: List[str], output_dir: str = None, debug: bool = False) -> List[Dict[str, Any]]:
    """
    Process multiple images and save results.
    
    Args:
        image_paths: List of image paths
        output_dir: Directory to save output images (if provided)
        debug: Enable debug output
        
    Returns:
        List of dictionaries with plate details
    """
    results = []
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    for idx, path in enumerate(image_paths):
        try:
            image = cv2.imread(path)
            if image is None:
                print(f"Error loading {path}")
                continue
            print(f"Processing {idx+1}/{len(image_paths)}: {os.path.basename(path)}")
            details = get_plate_details(image, debug)
            details["filename"] = os.path.basename(path)
            results.append(details)
            
            if output_dir and details["plate_text"]:
                output_path = os.path.join(output_dir, f"{details['plate_text']}_{details['filename']}")
                result_img = image.copy()
                cv2.putText(result_img, details["plate_text"], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(result_img, f"Raw: {details['raw_text'][:20]}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
                cv2.putText(result_img, f"Conf: {details['confidence']:.2f}, Valid: {details['valid']}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
                cv2.imwrite(output_path, result_img)
                print(f"Saved to {output_path}")
        except Exception as e:
            print(f"Error processing {path}: {e}")
    return results

if __name__ == "__main__":
    # Example usage
    images = ["path/to/image1.jpg", "path/to/image2.jpg"]
    results = batch_process_plates(images, "output", debug=True)
    for r in results:
        print(f"File: {r['filename']}, Plate: {r['plate_text']}, Valid: {r['valid']}")