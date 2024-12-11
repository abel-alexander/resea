import os
import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np


def pdf_to_images(pdf_path, dpi=300):
    """
    Converts a PDF file into a list of images.
    """
    return [np.array(page.convert('RGB')) for page in convert_from_path(pdf_path, dpi=dpi)]


def extract_text_with_coordinates(image):
    """
    Extracts text along with bounding box coordinates from an image using Tesseract OCR.
    """
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return data


def identify_numeric_columns(data, threshold=0.5):
    """
    Identifies areas with a high density of numbers organized in a columnar fashion.

    Parameters:
    - data: OCR results containing text and bounding box information.
    - threshold: Proportion of numeric entries required to classify a region as a table.

    Returns:
    - List of bounding boxes representing potential table regions.
    """
    num_entries = len(data['text'])
    numeric_boxes = []

    for i in range(num_entries):
        text = data['text'][i].strip()
        if text.replace('.', '', 1).isdigit():  # Check if the text is numeric
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            numeric_boxes.append((x, y, w, h))

    # Cluster boxes into columns by proximity and alignment
    rows = {}
    for x, y, w, h in numeric_boxes:
        row_key = y // 10  # Adjust row proximity threshold as needed
        if row_key not in rows:
            rows[row_key] = []
        rows[row_key].append((x, y, w, h))

    # Filter rows to find columns with sufficient numeric density
    table_regions = []
    for key, row in rows.items():
        if len(row) / num_entries > threshold:  # Check numeric density
            x_min = min(box[0] for box in row)
            y_min = min(box[1] for box in row)
            x_max = max(box[0] + box[2] for box in row)
            y_max = max(box[1] + box[3] for box in row)
            table_regions.append((x_min, y_min, x_max, y_max))

    return table_regions


def draw_bounding_boxes(image, regions, output_path):
    """
    Draws bounding boxes on an image to visualize detected table regions.

    Parameters:
    - image: The input image.
    - regions: List of bounding boxes (x1, y1, x2, y2).
    - output_path: Path to save the image with bounding boxes.
    """
    for (x1, y1, x2, y2) in regions:
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imwrite(output_path, image)


def extract_tables_from_pdf(pdf_path, output_dir):
    """
    Detects tables in a PDF by focusing on numeric regions and saves them as individual images.

    Parameters:
    - pdf_path: Path to the PDF file.
    - output_dir: Directory to save the detected table images.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert PDF to images
    images = pdf_to_images(pdf_path)

    for page_number, image in enumerate(images):
        # Convert image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Extract text with bounding boxes
        ocr_data = extract_text_with_coordinates(gray_image)

        # Identify numeric columns
        table_regions = identify_numeric_columns(ocr_data)

        # Draw bounding boxes for visualization
        output_image_path = os.path.join(output_dir, f"page_{page_number + 1}_detected_tables.png")
        draw_bounding_boxes(image, table_regions, output_image_path)
        print(f"Saved table visualization for page {page_number + 1} to {output_image_path}")


if __name__ == "__main__":
    # Specify the path to your PDF file and the output directory
    pdf_path = "path_to_your_pdf.pdf"  # Replace with your PDF file path
    output_dir = "detected_tables_output"  # Replace with your desired output directory

    extract_tables_from_pdf(pdf_path, output_dir)
