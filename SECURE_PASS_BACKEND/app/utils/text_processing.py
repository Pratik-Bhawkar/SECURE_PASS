# app/utils/text_processing.py
import re

def clean_plate_text(raw_text: str) -> str:
    """
    Basic cleanup: remove unwanted characters, 'IND', etc.
    """
    text = raw_text.upper()
    
    # Remove quotes and special characters except letters, digits, and spaces
    text = re.sub(r'[^A-Z0-9\s]', '', text)
    
    # Remove "IND"
    text = text.replace("IND", "")
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def filter_plate_format(cleaned_text: str) -> str:
    """
    Enforces the strict format:
    1) Two alphabets
    2) Two digits
    3) One or two alphabets
    4) Four digits
    
    If the text matches, return it; otherwise, return an empty string or fallback.
    """
    pattern = r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$'
    match = re.match(pattern, cleaned_text)
    if match:
        return match.group(0)  # The entire matched string
    else:
        return ""  # or some fallback like "INVALID"

def get_final_plate_text(raw_text: str) -> str:
    """
    Combines both cleaning and format filtering to return the final plate string
    or an empty string if no valid plate is found.
    """
    # Step 1: Basic cleanup
    cleaned = clean_plate_text(raw_text)
    # Step 2: Strict format check
    final_plate = filter_plate_format(cleaned)
    return final_plate
