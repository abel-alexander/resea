import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image
import re

def extract_text_via_ocr(pdf_path, pages=[0, 1]):
    """
    Extract text from the specified pages of a PDF using OCR.
    Args:
        pdf_path (str): Path to the PDF file.
        pages (list): List of page numbers to process.
    Returns:
        dict: Page number as key and extracted OCR text as value.
    """
    pdf = fitz.open(pdf_path)
    ocr_text = {}
    
    for page_num in pages:
        pix = pdf[page_num].get_pixmap()  # Render page to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        ocr_text[page_num + 1] = text  # Use 1-based page numbering

    pdf.close()
    return ocr_text


def process_toc_with_ocr(pdf_path):
    """
    Process the TOC using OCR-extracted text and associate hyperlinks.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        dict: Structured TOC with Level 1 and Level 2 groupings.
    """
    pdf = fitz.open(pdf_path)
    ocr_text = extract_text_via_ocr(pdf_path, pages=[0, 1])  # OCR for Page 1 & 2
    toc_structure = {}

    for page_num, text in ocr_text.items():
        print(f"OCR Text from Page {page_num}:\n{text}")  # Debug OCR output

        lines = text.split("\n")
        level1 = None  # Track current Level 1

        for line in lines:
            line = line.strip()
            if re.match(r"^\d+\.\s+.+", line):  # Match Level 1: e.g., '1. Birkenstock'
                level1 = line
                toc_structure[level1] = []
            elif re.match(r"^\s+\d+\s+.+", line):  # Match Level 2: indented titles
                if level1:
                    toc_structure[level1].append(line.strip())

    # Map hyperlinks sequentially to Level 2 items
    for page_num in range(2):  # Limit to Page 1 and Page 2
        links = pdf[page_num].get_links()
        link_pages = [link.get("page", None) for link in links if "page" in link]
        print(f"Links on Page {page_num + 1}: {link_pages}")  # Debug hyperlinks

        idx = 0
        for level1 in toc_structure:
            for i, item in enumerate(toc_structure[level1]):
                if idx < len(link_pages):
                    toc_structure[level1][i] = {"Title": item, "Page": link_pages[idx] + 1}
                    idx += 1

    pdf.close()
    return toc_structure


def print_clean_toc(toc_structure):
    """
    Print the TOC structure without page numbers for clean output.
    Args:
        toc_structure (dict): Structured TOC with Level 1 and Level 2 entries.
    """
    print("\nCleaned Table of Contents:")
    for level1, level2_items in toc_structure.items():
        print(level1)
        for item in level2_items:
            print(f"   - {item['Title']}")


def get_toc(toc_structure):
    """
    Return the structured Table of Contents in a format without page numbers.
    Args:
        toc_structure (dict): Structured TOC with Level 1 and Level 2 entries.
    Returns:
        dict: Cleaned TOC without page numbers.
    """
    clean_toc = {}
    for level1, level2_items in toc_structure.items():
        clean_toc[level1] = [item['Title'] for item in level2_items]
    return clean_toc


# === Usage ===
pdf_path = "your_pdf_path_here.pdf"  # Replace with your PDF file path

toc_structure = process_toc_with_ocr(pdf_path)

# Debug output
print_clean_toc(toc_structure)  # Output without page numbers
clean_toc = get_toc(toc_structure)  # Clean TOC for further use

print("\nget_toc Result:")
print(clean_toc)
