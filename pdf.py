# Install required libraries before running this code:
# pip install camelot-py[cv] pdfplumber pymupdf pytesseract opencv-python-headless pdf2image

import camelot
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# 1. Camelot - Structured PDFs
def extract_tables_camelot(pdf_path, pages="all", flavor="stream"):
    """
    Extract tables using Camelot.
    Args:
        pdf_path (str): Path to the PDF file.
        pages (str): Pages to extract tables from (default: 'all').
        flavor (str): 'stream' for loose tables, 'lattice' for grid-like tables.
    Returns:
        list: List of tables as pandas DataFrames.
    """
    tables = camelot.read_pdf(pdf_path, pages=pages, flavor=flavor)
    return [table.df for table in tables]  # Return tables as DataFrames


# 2. PDFplumber - Unstructured PDFs
def extract_tables_pdfplumber(pdf_path):
    """
    Extract tables using PDFplumber.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: List of tables as nested lists.
    """
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            if page_tables:
                print(f"Tables found on page {page_num + 1}")
            tables.extend(page_tables)
    return tables


# 3. PyMuPDF (fitz) - Fast Extraction of Text Blocks
def extract_tables_pymupdf(pdf_path):
    """
    Extract tables as text blocks using PyMuPDF.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: List of text blocks detected on each page.
    """
    tables = []
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        print(f"Text blocks on page {page_num + 1}:")
        for block in blocks:
            print(block)  # Each block contains coordinates and text
        tables.append(blocks)
    return tables


# 4. Tesseract + OpenCV - Scanned PDFs
def extract_tables_ocr(pdf_path, page_num=0):
    """
    Extract tables from scanned PDFs using OCR and OpenCV.
    Args:
        pdf_path (str): Path to the PDF file.
        page_num (int): Page number to process (0-indexed).
    Returns:
        str: Extracted text from the table.
    """
    # Convert PDF page to image
    images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
    image = np.array(images[0])

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Thresholding to clean up the image
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect table boundaries using dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Extract text using Tesseract
    text = pytesseract.image_to_string(dilated, config="--psm 6")
    return text


# ---------------- RUN THE FUNCTIONS ----------------
if __name__ == "__main__":
    pdf_path = "example.pdf"  # Change this to your PDF file path

    # 1. Extract tables with Camelot
    print("Extracting tables using Camelot...")
    camelot_tables = extract_tables_camelot(pdf_path, pages="1", flavor="stream")
    for idx, table in enumerate(camelot_tables):
        print(f"Camelot Table {idx + 1}:\n", table)

    # 2. Extract tables with PDFplumber
    print("\nExtracting tables using PDFplumber...")
    plumber_tables = extract_tables_pdfplumber(pdf_path)
    for idx, table in enumerate(plumber_tables):
        print(f"PDFplumber Table {idx + 1}:\n", table)

    # 3. Extract text blocks with PyMuPDF
    print("\nExtracting text blocks using PyMuPDF...")
    pymupdf_tables = extract_tables_pymupdf(pdf_path)

    # 4. Extract tables from scanned PDFs using OCR
    print("\nExtracting tables using Tesseract OCR...")
    ocr_table_text = extract_tables_ocr(pdf_path, page_num=0)
    print("OCR Extracted Table Text:\n", ocr_table_text)


import pandas as pd

def reconstruct_table_from_blocks(blocks):
    """
    Reconstruct a table-like structure from text blocks.
    Args:
        blocks (list): List of text blocks (x0, y0, x1, y1, text).
    Returns:
        pd.DataFrame: Table reconstructed from blocks.
    """
    # Sort blocks by y-coordinates (rows)
    blocks_sorted = sorted(blocks, key=lambda b: b[1])  # Sort by y0
    
    # Build table rows
    rows = []
    for block in blocks_sorted:
        rows.append(block[4])  # Extract text content

    # Split rows by spaces to simulate columns
    table = [row.split() for row in rows]
    return pd.DataFrame(table)

# Example usage
doc = fitz.open("example.pdf")
blocks = doc[0].get_text("blocks")  # Extract text blocks from page 0
table_df = reconstruct_table_from_blocks(blocks)
print(table_df)
