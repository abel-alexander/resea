import fitz  # PyMuPDF
import cv2
import numpy as np
import os

def pdf_to_images_pymupdf(pdf_path, output_folder="output_images"):
    """
    Convert PDF pages to images using PyMuPDF.
    Args:
        pdf_path (str): Path to the PDF file.
        output_folder (str): Folder to save the converted images.
    Returns:
        list: List of image file paths.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        # Render the page as an image
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths

def detect_table_with_opencv(image_path, output_folder="output_tables"):
    """
    Detect and extract table boundaries from an image using OpenCV.
    Args:
        image_path (str): Path to the input image.
        output_folder (str): Folder to save the detected tables.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Thresholding to get a binary image
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect horizontal and vertical lines using morphological operations
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine the detected lines
    table_structure = cv2.add(horizontal_lines, vertical_lines)

    # Find contours of the table
    contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours to highlight table boundaries
    result = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)  # Green color for tables

    # Save the result
    output_image_path = os.path.join(output_folder, os.path.basename(image_path).replace(".png", "_detected.png"))
    cv2.imwrite(output_image_path, result)
    print(f"Table detection saved at: {output_image_path}")

# ---------------- RUN THE PROCESS ----------------
if __name__ == "__main__":
    pdf_path = "example.pdf"  # Replace with your PDF file path
    output_folder_images = "output_images"  # Folder to store intermediate images
    output_folder_tables = "output_tables"  # Folder to save table-detected images

    # Step 1: Convert PDF pages to images using PyMuPDF
    print("Converting PDF to images...")
    image_paths = pdf_to_images_pymupdf(pdf_path, output_folder_images)

    # Step 2: Process each image with OpenCV to detect tables
    print("Detecting tables in images...")
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        detect_table_with_opencv(image_path, output_folder_tables)
