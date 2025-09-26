# app/utils/detection_utils.py
import cv2
from ultralytics import YOLO

def load_yolo_model(model_path: str = "./yolo_v8_custom_updated/weights/best.pt"):
    """
    Loads the custom YOLOv8 model from the specified path.
    """
    model = YOLO(model_path)
    return model

def detect_number_plate(image_path: str, model=None, conf_threshold: float = 0.25):
    """
    Detects objects in the image using YOLOv8 and returns detection results.
    Each detection is a dict with:
      - 'bbox': [xmin, ymin, xmax, ymax]
      - 'confidence': confidence score
      - 'class': predicted class index
    """
    if model is None:
        model = load_yolo_model()
    
    results = model(image_path, conf=conf_threshold)
    detections = []
    for result in results:
        for box in result.boxes:
            bbox = box.xyxy.tolist()[0]
            confidence = float(box.conf.item())
            cls = int(box.cls.item())
            detections.append({
                "bbox": bbox,
                "confidence": confidence,
                "class": cls
            })
    return detections

if __name__ == "__main__":
    from pathlib import Path
    
    # Use relative path for testing
    project_root = Path(__file__).parent.parent.parent
    test_image = project_root / "data" / "our database" / "WhatsApp Image 2025-03-19 at 11.31.54_d3bc5a3d.jpg"
    
    if test_image.exists():
        model = load_yolo_model()
        results = detect_number_plate(str(test_image), model=model)
        print("Detection Results:")
        for det in results:
            print(det)
    else:
        print(f"Test image not found: {test_image}")
