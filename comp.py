import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image
import re

def extract_text_via_ocr(pdf_path, page):
    """
    Extract text from a single PDF page using OCR.
    Args:
        pdf_path (str): Path to the PDF file.
        page (int): Page number to process.
    Returns:
        str: OCR-extracted text.
    """
    pdf = fitz.open(pdf_path)
    pix = pdf[page].get_pixmap()  # Render page to image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img)
    pdf.close()
    return text

def clean_toc_text(ocr_text):
    """
    Clean OCR text to extract meaningful TOC lines.
    Args:
        ocr_text (str): OCR-extracted text.
    Returns:
        list: Cleaned TOC lines.
    """
    lines = ocr_text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()
        # Match Level 1: "1. Birkenstock" or Level 2: "  1 Earnings Report"
        if re.match(r"^\d+\.\s+.+", line) or re.match(r"^\s+\d+\s+.+", line):
            clean_lines.append(line)
    return clean_lines

def parse_toc_hierarchy(clean_lines):
    """
    Parse TOC lines into a structured Level 1 and Level 2 hierarchy.
    Args:
        clean_lines (list): List of cleaned TOC lines.
    Returns:
        dict: Structured TOC with Level 1 and Level 2 groupings.
    """
    toc_structure = {}
    current_level1 = None

    for line in clean_lines:
        if re.match(r"^\d+\.\s+.+", line):  # Level 1: e.g., "1. Birkenstock"
            current_level1 = line
            toc_structure[current_level1] = []
        elif re.match(r"^\s+\d+\s+.+", line):  # Level 2: e.g., "   1 Earnings Report"
            if current_level1:
                toc_structure[current_level1].append(line.strip())

    return toc_structure

def process_toc(pdf_path):
    """
    Process the Table of Contents, prioritizing Page 1, then Page 2.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: Final structured TOC.
    """
    # Step 1: Extract OCR from Page 1
    ocr_text = extract_text_via_ocr(pdf_path, page=0)
    if "Table of Contents" not in ocr_text:
        # If not found on Page 1, go to Page 2
        ocr_text = extract_text_via_ocr(pdf_path, page=1)

    print("OCR Text:\n", ocr_text)  # Debugging: View raw OCR text

    # Step 2: Clean TOC text
    clean_lines = clean_toc_text(ocr_text)

    # Step 3: Parse into hierarchy
    toc_structure = parse_toc_hierarchy(clean_lines)

    return toc_structure

def print_clean_toc(toc_structure):
    """
    Print the TOC structure in a clean format.
    Args:
        toc_structure (dict): Structured TOC.
    """
    print("\nCleaned Table of Contents:")
    for level1, level2_items in toc_structure.items():
        print(level1)
        for item in level2_items:
            print(f"   - {item}")


def get_toc(toc_structure):
    """
    Return TOC in a dictionary format.
    Args:
        toc_structure (dict): Structured TOC.
    Returns:
        dict: Cleaned TOC without page numbers.
    """
    return {level1: level2_items for level1, level2_items in toc_structure.items()}


# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF path

# Step 1: Process TOC
toc_structure = process_toc(pdf_path)

# Step 2: Display Cleaned TOC
print_clean_toc(toc_structure)

# Step 3: Use TOC Structure
clean_toc = get_toc(toc_structure)
print("\nget_toc Result:")
print(clean_toc)
