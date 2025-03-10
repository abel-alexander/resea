import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import re

def extract_text_with_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    
    toc_text = []
    found_toc = False
    end_text = "BofA SECURITIES"  # Expected end marker

    for page in doc:
        text = page.get_text("text")  # Extract selectable text
        if "Table of Contents" in text:
            found_toc = True
        
        if found_toc:
            toc_text.append(text)
        
        if end_text in text:  # Stop extracting after "BofA SECURITIES"
            break

    extracted_text = "\n".join(toc_text).strip()

    # If PyMuPDF didn't find BofA SECURITIES, use OCR
    if end_text not in extracted_text:
        print("Switching to OCR for full extraction...")
        images = convert_from_path(pdf_path, first_page=0, last_page=2)  # Convert first few pages to images
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img) + "\n"

        # Merge OCR and PyMuPDF results (remove duplicates)
        if "Table of Contents" in ocr_text:
            extracted_text = ocr_text  # Use OCR if it has more content

    return extracted_text

# Example usage
pdf_path = "your_file.pdf"
extracted_text = extract_text_with_ocr(pdf_path)
print(extracted_text)  # Now process this further for ToC extraction
