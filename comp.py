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
        list: Combined OCR text from left and right columns.
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

def clean_line(line):
    """
    Remove dates or parenthesis like (3.5.2024) from a line.
    Args:
        line (str): Input line.
    Returns:
        str: Cleaned line without dates or parentheses.
    """
    return re.sub(r"\(.*?\)", "", line).strip()

def identify_toc_entries(lines):
    """
    Identify Level 1 and Level 2 entries and preserve hierarchy.
    Args:
        lines (list): List of lines from OCR text.
    Returns:
        dict: Structured TOC with Level 1 as keys and Level 2 as child entries.
    """
    toc_structure = {}
    current_level1 = None

    # Regex patterns
    level1_pattern = r"^\d+\.\s"  # Matches Level 1 (e.g., '1. Recent Earnings')
    level2_pattern = r"^\s*[ivxlc]+\.\s"  # Matches Level 2 (e.g., 'i. Q1 2024...')

    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Check for Level 1
        if re.match(level1_pattern, line):
            current_level1 = clean_line(line)
            toc_structure[current_level1] = []
        # Check for Level 2 under the current Level 1
        elif current_level1 and re.match(level2_pattern, line):
            toc_structure[current_level1].append(clean_line(line))

    return toc_structure

def extract_toc_below_title(lines):
    """
    Extract TOC lines that appear after 'Table of Contents'.
    Args:
        lines (list): List of lines extracted from OCR.
    Returns:
        dict: Structured TOC with Level 1 and Level 2 entries.
    """
    process_lines = False
    toc_lines = []

    for line in lines:
        line = line.strip()
        if "Table of Contents" in line:
            process_lines = True
            continue

        if process_lines and line:
            toc_lines.append(line)

    return identify_toc_entries(toc_lines)

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
    for page_num in [0, 1]:  # Check Page 1, fallback to Page 2
        left_lines, right_lines = extract_text_from_columns(pdf_path, page=page_num)
        combined_lines = merge_columns(left_lines, right_lines)

        if any("Table of Contents" in line for line in combined_lines):
            print(f"TOC Found on Page {page_num + 1}")
            return extract_toc_below_title(combined_lines)

    print("Table of Contents not found.")
    return {}

def print_clean_toc(toc_structure):
    """
    Print the TOC structure in a clean format.
    Args:
        toc_structure (dict): Structured TOC.
    """
    print("\nCleaned Table of Contents:")
    for level1, level2 in toc_structure.items():
        print(level1)
        for child in level2:
            print(f"   - {child}")

# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF file path

# Step 1: Process TOC dynamically
toc_structure = process_toc(pdf_path)

# Step 2: Display and use TOC
print_clean_toc(toc_structure)
