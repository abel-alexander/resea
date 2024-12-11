import cv2
import pytesseract
import logging
import re
import fitz  # PyMuPDF
import numpy as np
from typing import List, Tuple, Any

def pdf_to_images(pdf_path: str) -> List[Any]:
    """
    Converts PDF pages to grayscale images using PyMuPDF.
    """
    try:
        logging.info("Converting PDF to images.")
        pdf_document = fitz.open(pdf_path)
        images = []

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            images.append(gray_image)

        pdf_document.close()
        logging.info("PDF converted to images successfully.")
        return images

    except Exception as e:
        logging.error("Error converting PDF to images", exc_info=True)
        raise

def detect_tables(image: Any) -> List[Tuple[int, int, int, int]]:
    """
    Detects tables in an image using morphological transformations and contour detection.
    """
    try:
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, image.shape[0] // 30))
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (image.shape[1] // 30, 1))

        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        table_grid = cv2.add(horizontal_lines, vertical_lines)
        contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        tables = [
            cv2.boundingRect(contour)
            for contour in contours
            if cv2.contourArea(contour) > image.size * 0.001
        ]

        logging.info(f"Detected {len(tables)} tables in the image.")
        return tables

    except Exception as e:
        logging.error("Error during table detection", exc_info=True)
        raise

def extract_text_from_tables(image: Any, tables: List[Tuple[int, int, int, int]]) -> List[str]:
    """
    Extracts text from specified table regions in an image using OCR.
    """
    try:
        texts = [
            pytesseract.image_to_string(image[y:y + h, x:x + w], lang='eng')
            for x, y, w, h in tables
        ]
        logging.info(f"Extracted text from {len(tables)} tables.")
        return texts

    except Exception as e:
        logging.error("Error extracting text from tables", exc_info=True)
        raise

def extract_tables_and_text(pdf_path: str) -> List[str]:
    """
    Extracts tables and their respective text from the document specified by the given PDF path.
    """
    try:
        logging.info("Starting table and text extraction process.")
        images = pdf_to_images(pdf_path)

        all_tables_text = []
        for image in images:
            tables = detect_tables(image)
            texts = extract_text_from_tables(image, tables)
            all_tables_text.extend(texts)

        logging.info("Completed table and text extraction process.")
        return all_tables_text

    except Exception as e:
        logging.error("Error in extracting tables and text", exc_info=True)
        raise

def extracted_data(pdf_path: str) -> List[str]:
    """
    Cleans and returns the extracted text data from tables in the document.
    """
    try:
        logging.info("Starting extracted data processing.")
        raw_texts = extract_tables_and_text(pdf_path)

        cleaned_texts = [
            re.sub(r'\s+', ' ', text.strip()) for text in raw_texts
        ]
        logging.info("Completed data extraction and cleaning.")
        return cleaned_texts

    except Exception as e:
        logging.error("Error in extracting data", exc_info=True)
        raise

# Example Call
# Uncomment and provide the path to your PDF file
# pdf_path = "path_to_your_pdf_file.pdf"
# extracted_texts = extracted_data(pdf_path)
# print(extracted_texts)
