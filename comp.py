import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image
import re

def extract_text_from_columns(pdf_path, page):
    """
    Extract text separately from left and right columns of a PDF page using OCR.
    Args:
        pdf_path (str): Path to the PDF file.
        page (int): Page number to process.
    Returns:
        tuple: OCR text from the left and right columns.
    """
    pdf = fitz.open(pdf_path)
    pix = pdf[page].get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Split into left and right halves
    left_half = img.crop((0, 0, img.width // 2, img.height))
    right_half = img.crop((img.width // 2, 0, img.width, img.height))

    # OCR for left and right halves
    left_text = pytesseract.image_to_string(left_half)
    right_text = pytesseract.image_to_string(right_half)

    pdf.close()
    return left_text, right_text

def clean_toc_text(text):
    """
    Clean OCR text to extract meaningful TOC lines.
    Args:
        text (str): OCR-extracted text.
    Returns:
        list: Cleaned TOC lines.
    """
    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()
        # Match Level 1 and Level 2: "1. Birkenstock" or "1 Earnings Report"
        if re.match(r"^\d+\.\s+.+", line) or re.match(r"^\s*\d+\s+.+", line):
            clean_lines.append(line)
    return clean_lines

def parse_toc_hierarchy(column_text):
    """
    Parse TOC lines into a structured Level 1 and Level 2 hierarchy for a column.
    Args:
        column_text (str): OCR-extracted text from a column.
    Returns:
        dict: Structured TOC for the column.
    """
    toc_structure = {}
    current_level1 = None
    lines = clean_toc_text(column_text)

    for line in lines:
        if re.match(r"^\d+\.\s+.+", line):  # Level 1: "1. Birkenstock"
            current_level1 = line
            toc_structure[current_level1] = []
        elif re.match(r"^\s*\d+\s+.+", line):  # Level 2: "1 Earnings Report"
            if current_level1:
                toc_structure[current_level1].append(line.strip())
    return toc_structure

def merge_toc(left_toc, right_toc):
    """
    Merge TOC structures from left and right columns.
    Args:
        left_toc (dict): TOC from the left column.
        right_toc (dict): TOC from the right column.
    Returns:
        dict: Combined TOC preserving order.
    """
    merged_toc = left_toc.copy()
    merged_toc.update(right_toc)  # Append right column TOC after left column
    return merged_toc

def process_toc(pdf_path):
    """
    Process the Table of Contents from a PDF page with two columns.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: Final structured TOC.
    """
    # Step 1: Extract text from Page 1 and fallback to Page 2
    for page_num in [0, 1]:
        left_text, right_text = extract_text_from_columns(pdf_path, page=page_num)

        if "Table of Contents" in left_text or "Table of Contents" in right_text:
            print(f"TOC Found on Page {page_num + 1}")
            left_toc = parse_toc_hierarchy(left_text)
            right_toc = parse_toc_hierarchy(right_text)
            return merge_toc(left_toc, right_toc)

    print("Table of Contents not found.")
    return {}

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
    Return the structured TOC in a clean dictionary format.
    Args:
        toc_structure (dict): Structured TOC.
    Returns:
        dict: Clean TOC.
    """
    return toc_structure


# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF path

# Step 1: Process TOC dynamically
toc_structure = process_toc(pdf_path)

# Step 2: Display and use TOC
print_clean_toc(toc_structure)
clean_toc = get_toc(toc_structure)

print("\nget_toc Result:")
print(clean_toc)
