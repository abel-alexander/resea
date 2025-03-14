import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re

def find_toc_page(pdf_path):
    """Scans the first three pages and returns the page number with the most hyperlinks."""
    doc = fitz.open(pdf_path)
    max_links = 0
    toc_page = 0  # Default to first page if no links found

    for page_num in range(min(3, len(doc))):  # Check first 3 pages
        links = doc[page_num].get_links()
        if len(links) > max_links:
            max_links = len(links)
            toc_page = page_num  # Update page with most links

    return toc_page

def extract_left_column_ocr(doc, toc_page):
    """Extracts text from the left column using OCR."""
    page = doc[toc_page]
    pix = page.get_pixmap()  # Convert page to an image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Crop only the left column (adjust x-coordinates if needed)
    left_column = img.crop((0, 0, img.width // 2, img.height))

    # Perform OCR
    ocr_text = pytesseract.image_to_string(left_column)

    return ocr_text

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    # Find the ToC page
    toc_page = find_toc_page(pdf_path)

    # Extract page numbers from the ToC page
    toc_page_links = doc[toc_page].get_links()
    page_numbers = [int(link["page"]) + 1 for link in toc_page_links if "page" in link]

    # Extract the left column using OCR
    left_column_text = extract_left_column_ocr(doc, toc_page)

    # Fix unwanted newlines breaking section names
    left_column_text = re.sub(r"(\d+\.|[ivxlc]+\.)\n", r"\1 ", left_column_text, flags=re.IGNORECASE)

    # Split into lines and extract structure
    toc_list = []
    for line in left_column_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Determine hierarchy level
        if re.match(r"^\d+\.", line):  # Main section
            level = 1
        elif re.match(r"^\d+\.", line) and len(toc_list) > 0:  # Sub-section
            level = 2
        else:
            continue  # Skip unrelated text

        # Clean section name
        section_name = re.sub(r"^\d+\.", "", line).strip()  # Remove numbering
        section_name = re.sub(r"^[ivxlc]+\.", "", section_name, re.IGNORECASE).strip()  # Remove Roman numerals
        section_name = re.sub(r"\d{4}\.\d{2}\.\d{2}\s–", "", section_name).strip()  # Remove dates

        # Add to ToC list (page number to be mapped later)
        toc_list.append([level, section_name, None])

    # Assign page numbers sequentially
    page_index = 0
    for i in range(len(toc_list)):
        if page_index < len(page_numbers):
            toc_list[i][2] = page_numbers[page_index]  # Assign page number
            page_index += 1  # Move to next available page number

    return toc_list

# Example usage
pdf_path = "your_file.pdf"
toc_output = extract_toc_from_pdf(pdf_path)

# Print structured output
for item in toc_output:
    print(item)  # Example: [1, 'Birkenstock', 3]
