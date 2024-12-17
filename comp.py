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
        list: OCR text from left and right columns.
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
    return left_text.split("\n"), right_text.split("\n")

def identify_toc_entries(lines):
    """
    Identify Level 1 entries based on the first 5 characters and handle split lines.
    Args:
        lines (list): List of lines from OCR text.
    Returns:
        dict: Structured TOC with Level 1 entries.
    """
    toc_structure = {}
    current_level1 = None

    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Check the first 5 characters for valid Level 1 patterns
        if len(line) >= 5 and re.match(r"^\d+\.\s", line[:5]):
            current_level1 = line
            toc_structure[current_level1] = []
        # Append split lines to the last Level 1 entry
        elif current_level1 and len(line) > 3:
            toc_structure[current_level1].append(line)

    return toc_structure

def merge_columns(left_lines, right_lines):
    """
    Merge TOC entries from two columns.
    Args:
        left_lines (list): TOC lines from the left column.
        right_lines (list): TOC lines from the right column.
    Returns:
        list: Combined lines from both columns.
    """
    return left_lines + right_lines

def process_toc(pdf_path):
    """
    Process TOC dynamically from a PDF with two-column handling.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: Final structured TOC.
    """
    for page_num in [0, 1]:  # Prioritize Page 1, then Page 2
        left_lines, right_lines = extract_text_from_columns(pdf_path, page=page_num)
        combined_lines = merge_columns(left_lines, right_lines)

        if any("Table of Contents" in line for line in combined_lines):
            print(f"TOC Found on Page {page_num + 1}")
            return identify_toc_entries(combined_lines)

    print("Table of Contents not found.")
    return {}

def print_clean_toc(toc_structure):
    """
    Print the TOC structure in a clean format.
    Args:
        toc_structure (dict): Structured TOC.
    """
    print("\nCleaned Table of Contents:")
    for idx, (level1, details) in enumerate(toc_structure.items(), 1):
        print(f"{idx}. {level1}")
        for detail in details:
            print(f"   - {detail}")

def get_toc(toc_structure):
    """
    Return the TOC structure as a clean dictionary.
    Args:
        toc_structure (dict): Structured TOC.
    Returns:
        dict: Clean TOC.
    """
    return toc_structure

# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF file path

# Step 1: Process TOC dynamically
toc_structure = process_toc(pdf_path)

# Step 2: Display and use TOC
print_clean_toc(toc_structure)
clean_toc = get_toc(toc_structure)

print("\nget_toc Result:")
print(clean_toc)
