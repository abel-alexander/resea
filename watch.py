import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
import io

def is_text_page(page):
    text = page.get_text()
    return bool(text.strip())

def ocr_image(image):
    return pytesseract.image_to_string(image)

def convert_pdf_page_to_image(page):
    pix = page.get_pixmap()
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return image

def extract_text_from_section(pdf_document, start_page, end_page, ocr=False):
    section_text = ""

    for page_num in range(start_page - 1, end_page):
        page = pdf_document.load_page(page_num)
        if is_text_page(page):
            section_text += page.get_text()
        elif ocr:
            image = convert_pdf_page_to_image(page)
            section_text += ocr_image(image)
    
    return section_text

def extract_and_save_text(document_sections, output_base_path):
    for doc_info in document_sections:
        file_path = doc_info['file_path']
        sections = doc_info['sections']
        pdf_document = fitz.open(file_path)

        for section in sections:
            title = section['title']
            start_page = section['start_page']
            end_page = section['end_page']
            ocr = section.get('ocr', False)

            # Create directory for the section if it doesn't exist
            section_dir = os.path.join(output_base_path, title)
            os.makedirs(section_dir, exist_ok=True)

            # Extract text from the section
            section_text = extract_text_from_section(pdf_document, start_page, end_page, ocr=ocr)

            # Save the extracted text to a file within the section directory
            document_name = os.path.basename(file_path).replace('.pdf', '.txt')
            output_file_path = os.path.join(section_dir, document_name)
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(section_text)
            print(f"Extracted text for section '{title}' in document '{file_path}' saved as '{output_file_path}'")

# Example usage
document_sections = [
    {
        'file_path': 'doc1.pdf',
        'sections': [
            {'title': 'Section A', 'start_page': 2, 'end_page': 5, 'ocr': True},
            {'title': 'Section B', 'start_page': 6, 'end_page': 10, 'ocr': False},
        ]
    },
    {
        'file_path': 'doc2.pdf',
        'sections': [
            {'title': 'Section A', 'start_page': 4, 'end_page': 8, 'ocr': True},
            {'title': 'Section C', 'start_page': 9, 'end_page': 12, 'ocr': False},
        ]
    },
    # Add more documents and sections as needed
]

output_base_path = 'output_sections'
extract_and_save_text(document_sections, output_base_path)
