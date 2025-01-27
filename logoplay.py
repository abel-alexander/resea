import cv2
import numpy as np
from ultralyticsplus import YOLO, render_result
from PIL import Image
import pytesseract  # OCR library

# Load the YOLO model
model = YOLO('keremberke/yolov8m-table-extraction')

# Set model parameters
model.overrides['conf'] = 0.25  # NMS confidence threshold
model.overrides['iou'] = 0.45  # NMS IoU threshold
model.overrides['agnostic_nms'] = False  # NMS class-agnostic
model.overrides['max_det'] = 1000  # maximum number of detections per image

# Set the image
image_path = 'zidane.jpg'  # Replace with your local image path
image = cv2.imread(image_path)  # Load the image as a numpy array

# Perform inference
results = model.predict(image)

# Visualize results
render = render_result(model=model, image=image, result=results[0])
render.show()

# Extract bounding boxes and text
for box in results[0].boxes:
    # Get bounding box coordinates
    xyxy = box.xyxy.cpu().numpy().astype(int)  # Convert to integers
    x_min, y_min, x_max, y_max = xyxy[0]

    # Crop the detected region
    cropped_region = image[y_min:y_max, x_min:x_max]

    # Convert to PIL Image for OCR
    pil_image = Image.fromarray(cv2.cvtColor(cropped_region, cv2.COLOR_BGR2RGB))

    # Perform OCR using pytesseract
    extracted_text = pytesseract.image_to_string(pil_image)

    # Display the extracted text
    print(f"Bounding Box: ({x_min}, {y_min}, {x_max}, {y_max})")
    print("Extracted Text:")
    print(extracted_text)
    print("-" * 50)
