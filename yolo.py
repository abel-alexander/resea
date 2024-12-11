import os
from pdf2image import convert_from_path
import cv2
import torch
from PIL import Image
from torchvision import transforms

# YOLO imports
from ultralytics import YOLO  # Ensure you have ultralytics package installed

# Function to convert a range of PDF pages to images
def pdf_pages_to_images(pdf_path, start_page, end_page):
    images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
    image_paths = []
    for i, image in enumerate(images, start=start_page):
        image_path = f"page_{i}.jpg"
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    return image_paths

# Table Detection using YOLO
def yolo_table_detection(image_path, model_path):
    # Load the YOLO model
    model = YOLO(model_path)

    # Perform table detection
    results = model(image_path)

    print("YOLO Table Detection Output:")
    for result in results:  # Iterate over results for the image
        for box in result.boxes:
            print(f"Bounding Box: {box.xyxy.tolist()} | Confidence: {box.confidence.item()} | Class: {box.cls.item()}")

    # Visualize the detection results
    annotated_image = results[0].plot()  # Annotated image with bounding boxes
    output_image_path = image_path.replace('.jpg', '_yolo_detected.jpg')
    cv2.imwrite(output_image_path, annotated_image)
    print(f"Annotated image saved at {output_image_path}")

# Main Script
def main():
    pdf_path = input("Enter the path to the PDF: ")
    start_page = int(input("Enter the starting page number: "))
    end_page = int(input("Enter the ending page number: "))
    model_path = input("Enter the path to the YOLO model file: ")

    # Convert PDF pages to images
    image_paths = pdf_pages_to_images(pdf_path, start_page, end_page)
    print(f"Converted pages {start_page}-{end_page} to images.")

    # Run table detection on each image
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        yolo_table_detection(image_path, model_path)

if __name__ == "__main__":
    main()
