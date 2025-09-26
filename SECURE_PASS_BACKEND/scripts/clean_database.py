# scripts/clean_database.py

import os
import sys
import time
import shutil
import easyocr

# Append the project root directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import RAW_DATA_DIR, CLEANED_DATA_DIR, TRASH_DATA_DIR

# Ensure destination directories exist
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)
os.makedirs(TRASH_DATA_DIR, exist_ok=True)

# Initialize EasyOCR reader (using GPU if available)
reader = easyocr.Reader(['en'], gpu=True)

def extract_text(image_path):
    """
    Attempts OCR on the provided image and returns the extracted text.
    """
    try:
        result = reader.readtext(image_path, detail=0, paragraph=True)
        # Join the OCR results into a single string
        return " ".join(result).strip() if result else ""
    except Exception as e:
        print(f"Error during OCR for {image_path}: {e}")
        return ""

def clean_images():
    # Accepted file extensions
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    # List all files in the RAW_DATA_DIR
    for filename in os.listdir(RAW_DATA_DIR):
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(RAW_DATA_DIR, filename)
            print(f"\nProcessing {filename}...")
            success = False
            
            # Attempt OCR up to 3 times
            for attempt in range(1, 4):
                text = extract_text(file_path)
                if text:
                    print(f"Attempt {attempt}: Success - Extracted text: '{text}'")
                    success = True
                    break
                else:
                    print(f"Attempt {attempt}: OCR failed.")
                    time.sleep(1)  # Optional delay between attempts
            
            # Move the file based on the OCR result
            if success:
                destination = os.path.join(CLEANED_DATA_DIR, filename)
                shutil.move(file_path, destination)
                print(f"Moved {filename} to CLEANED folder.")
            else:
                destination = os.path.join(TRASH_DATA_DIR, filename)
                shutil.move(file_path, destination)
                print(f"Moved {filename} to TRASH folder (failed OCR after 3 attempts).")

if __name__ == "__main__":
    clean_images()
