import pdfplumber
import fitz  # PyMuPDF
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
import pytesseract
from PIL import Image
from io import BytesIO

# Function to extract text using pdfminer.six
def extract_with_pdfminer(pdf_path):
    try:
        text = pdfminer_extract_text(pdf_path)
        with open("output_pdfminer.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Extracted text using pdfminer.six saved to output_pdfminer.txt")
    except Exception as e:
        print(f"pdfminer.six extraction failed: {e}")

# Function to extract text using pdfplumber
def extract_with_pdfplumber(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        with open("output_pdfplumber.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Extracted text using pdfplumber saved to output_pdfplumber.txt")
    except Exception as e:
        print(f"pdfplumber extraction failed: {e}")

# Function to extract text using PyMuPDF
def extract_with_pymupdf(pdf_path):
    try:
        text = ""
        with fitz.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf, start=1):
                blocks = page.get_text("blocks")
                blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # Sort blocks by y, then x
                page_text = "\n".join([block[4] for block in blocks])
                text += f"\n--- Page {page_num} ---\n" + page_text
        with open("output_pymupdf.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Extracted text using PyMuPDF saved to output_pymupdf.txt")
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")

# Function to extract text using PyPDF2
def extract_with_pypdf2(pdf_path):
    try:
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or "" + "\n"
        with open("output_pypdf2.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Extracted text using PyPDF2 saved to output_pypdf2.txt")
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")

# Function to extract text using OCR with PyMuPDF and pytesseract
def extract_with_ocr(pdf_path):
    try:
        text = ""
        with fitz.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf, start=1):
                pix = page.get_pixmap()
                img = Image.open(BytesIO(pix.tobytes()))
                ocr_text = pytesseract.image_to_string(img)
                text += f"\n--- OCR Page {page_num} ---\n" + ocr_text
        with open("output_ocr.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Extracted text using OCR saved to output_ocr.txt")
    except Exception as e:
        print(f"OCR extraction failed: {e}")

# Main function to perform all extractions
def extract_all_methods(pdf_path):
    print(f"Extracting from {pdf_path} using various methods...")
    extract_with_pdfminer(pdf_path)
    extract_with_pdfplumber(pdf_path)
    extract_with_pymupdf(pdf_path)
    extract_with_pypdf2(pdf_path)
    extract_with_ocr(pdf_path)
    print("Extraction completed. Check the output text files for comparison.")

# Provide the path to your PDF file
pdf_path = "/Users/amruthaantony/PycharmProjects/data_extraction/pib1.pdf"
extract_all_methods(pdf_path)
