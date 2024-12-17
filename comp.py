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

def extract_toc_below_title(lines):
    """
    Extract TOC lines that appear after 'Table of Contents' and start with indexing.
    Args:
        lines (list): List of lines extracted from OCR.
    Returns:
        list: Cleaned TOC entries with original indexing.
    """
    toc_entries = []
    process_lines = False

    for line in lines:
        line = line.strip()

        # Start processing only after encountering 'Table of Contents'
        if "Table of Contents" in line:
            process_lines = True
            continue

        if not process_lines or not line:
            continue

        # Only include lines starting with indexing like '1.', '2.', etc.
        if re.match(r"^\d+\.\s", line):  # Strict pattern for valid Level 1
            cleaned_line = clean_line(line)
            toc_entries.append(cleaned_line)

    return toc_entries

def process_toc(pdf_path):
    """
    Process TOC dynamically from a PDF with two-column handling.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        list: Final TOC entries as extracted.
    """
    for page_num in [0, 1]:  # Check Page 1, fallback to Page 2
        left_lines, right_lines = extract_text_from_columns(pdf_path, page=page_num)
        combined_lines = left_lines + right_lines

        if any("Table of Contents" in line for line in combined_lines):
            print(f"TOC Found on Page {page_num + 1}")
            return extract_toc_below_title(combined_lines)

    print("Table of Contents not found.")
    return []

# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF file path

# Step 1: Process TOC dynamically
toc_entries = process_toc(pdf_path)

# Step 2: Display and use TOC
print("\nCleaned Table of Contents:")
for entry in toc_entries:
    print(entry)
