from pdf2image import convert_from_path
from ultralytics import YOLO
import cv2
import os

# Function to convert PDF pages to images
def pdf_to_images(pdf_path, output_folder, dpi=300):
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)
    os.makedirs(output_folder, exist_ok=True)
    image_paths = []

    for i, page in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        page.save(image_path, "JPEG")
        image_paths.append(image_path)
        print(f"Saved: {image_path}")

    return image_paths

# Function to perform YOLOv3 table detection on images
def detect_tables_in_images(image_paths, model_path, output_folder):
    # Load YOLOv3 model
    model = YOLO(model_path)
    os.makedirs(output_folder, exist_ok=True)

    for image_path in image_paths:
        # Perform inference
        results = model.predict(image_path)
        
        # Save results (image with bounding boxes)
        output_path = os.path.join(output_folder, os.path.basename(image_path))
        for result in results:  # Loop through results (supporting multiple pages)
            annotated_image = result.plot()
            cv2.imwrite(output_path, annotated_image)
            print(f"Saved detection result to: {output_path}")
        
        # Optionally, extract bounding boxes or save cropped tables
        for detection in results:
            for box in detection.boxes.xyxy:  # Bounding box coordinates
                x1, y1, x2, y2 = map(int, box)
                print(f"Detected Table: [{x1}, {y1}, {x2}, {y2}]")

# Paths and configurations
pdf_path = "path/to/your/input.pdf"  # Replace with the path to your PDF
output_image_folder = "output_images"  # Folder to save images
output_detection_folder = "output_detections"  # Folder to save detection results
yolov3_model_path = "path/to/yolov3u.pt"  # Replace with your YOLOv3 model file

# Step 1: Convert PDF to images
image_paths = pdf_to_images(pdf_path, output_image_folder)

# Step 2: Perform YOLOv3 detection on images
detect_tables_in_images(image_paths, yolov3_model_path, output_detection_folder)
