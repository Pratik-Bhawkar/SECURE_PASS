import sys
import os

# Add the project root directory (one level up from scripts) to sys.path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import os
import glob
import random
from app.core.database import SessionLocal
from app.core.models import AuthorizedVehicle
from app.utils.detection_utils import detect_number_plate
from app.utils.ocr_utils import crop_image, ocr_plate
from app.utils.text_processing import process_plate_text

# Define a list of random names to assign to bike owners (or bikes)
RANDOM_NAMES = [
    "Mahesh", "Raj", "Tushar", "Sahil", "Riya",
    "Devika", "Shrawani", "Atharva", "Shreyash", "Viraj"
]

def import_authorized_vehicles(images_folder: str):
    """
    Iterates over all images in the given folder, extracts the number plate,
    processes the text, and inserts it into the AuthorizedVehicle table if not already present.
    Each inserted record is assigned a random name and a vehicle type of "Bike".
    """
    db = SessionLocal()
    # Loop over all images (supports jpg, jpeg, png)
    image_paths = glob.glob(os.path.join(images_folder, '*.*'))
    for image_path in image_paths:
        print(f"\nProcessing image: {image_path}")
        # Use the detection pipeline to extract bounding boxes
        detections = detect_number_plate(image_path)
        if not detections:
            print("  No detections found. Skipping image.")
            continue
        
        # Assume the first detection is the number plate.
        detection = detections[0]
        bbox = detection.get("bbox")
        
        try:
            # Crop the image to the detected plate region
            cropped = crop_image(image_path, bbox)
        except Exception as e:
            print(f"  Error cropping image: {e}")
            continue
        
        # Run OCR on the cropped image (debug flag can be set to False)
        raw_text = ocr_plate(cropped, debug=False)
        print(f"  Raw OCR output: '{raw_text}'")
        
        # Process the raw OCR text to extract a clean plate number
        processed_text = process_plate_text(raw_text)
        print(f"  Processed plate text: '{processed_text}'")
        
        if not processed_text:
            print("  Could not extract a valid plate text. Skipping image.")
            continue
        
        # Check if the plate already exists in the database
        vehicle = db.query(AuthorizedVehicle).filter(
            AuthorizedVehicle.plate_number == processed_text
        ).first()
        if vehicle:
            print(f"  Plate '{processed_text}' already exists. Skipping.")
        else:
            # Select a random name from the list
            random_name = random.choice(RANDOM_NAMES)
            # Insert the new authorized vehicle record with vehicle_type "Bike"
            new_vehicle = AuthorizedVehicle(
                plate_number=processed_text,
                owner_name=random_name,
                vehicle_type="Bike"
            )
            db.add(new_vehicle)
            db.commit()
            print(f"  Added authorized vehicle with plate: '{processed_text}', owner: '{random_name}', type: 'Bike'")
    db.close()

if __name__ == "__main__":
    # Set the path to your authorized vehicle images folder
    images_folder = "C:/Users/PRATIK/SECURE_PASS_BACKEND/data/our database"
    import_authorized_vehicles(images_folder)
