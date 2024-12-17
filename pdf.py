from pdf2image import convert_from_path
import cv2
import numpy as np
import os

def pdf_to_images(pdf_path, output_folder="output_images"):
    """
    Convert PDF pages into images using pdf2image.
    Args:
        pdf_path (str): Path to the input PDF file.
        output_folder (str): Folder to save the converted images.
    Returns:
        list: List of image file paths.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert PDF pages to images
    images = convert_from_path(pdf_path)
    image_paths = []

    # Save each page as an image
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i + 1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

def detect_table_with_opencv(image_path):
    """
    Detect and extract table boundaries from an image using OpenCV.
    Args:
        image_path (str): Path to the input image.
    """
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply thresholding to create a binary image
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect horizontal and vertical lines using morphological operations
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine horizontal and vertical lines to get the table structure
    table_structure = cv2.add(horizontal_lines, vertical_lines)

    # Find contours of the table
    contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw the detected contours
    result = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)

    # Save and display the result
    output_path = image_path.replace(".png", "_detected.png")
    cv2.imwrite(output_path, result)
    print(f"Table detection saved at: {output_path}")

# ---------------- RUN THE PROCESS ----------------
if __name__ == "__main__":
    # Input PDF path
    pdf_path = "example.pdf"  # Replace with your PDF file path

    # Step 1: Convert PDF pages to images
    print("Converting PDF to images...")
    image_paths = pdf_to_images(pdf_path)

    # Step 2: Process each image for table detection
    print("Detecting tables in images...")
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        detect_table_with_opencv(image_path)
