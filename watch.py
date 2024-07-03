import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
import io

def ocr_image(image):
    return pytesseract.image_to_string(image)

def convert_pdf_to_images(pdf_path, start_page, end_page, output_folder):
    pdf_document = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(start_page - 1, end_page):
        if page_num < 0 or page_num >= pdf_document.page_count:
            print(f"Page number {page_num} is out of range")
            continue

        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        image.save(image_path)
        image_paths.append(image_path)
        print(f"Page {page_num + 1} saved as {image_path}")

    return image_paths

def extract_text_from_images(image_paths, output_folder):
    section_text = ""

    for image_path in image_paths:
        image = Image.open(image_path)
        section_text += ocr_image(image)

    text_path = os.path.join(output_folder, 'extracted_text.txt')
    with open(text_path, 'w', encoding='utf-8') as file:
        file.write(section_text)
    print(f"Extracted text saved as {text_path}")

def extract_and_save_text(document_sections, output_base_path):
    for doc_info in document_sections:
        file_path = doc_info['file_path']
        sections = doc_info['sections']
        pdf_document = fitz.open(file_path)

        for section in sections:
            title = section['title']
            start_page = section['start_page']
            end_page = section['end_page']

            # Create directory for the section if it doesn't exist
            section_dir = os.path.join(output_base_path, title)
            os.makedirs(section_dir, exist_ok=True)

            # Convert PDF pages to images
            image_paths = convert_pdf_to_images(file_path, start_page, end_page, section_dir)

            # Extract text from images and save
            extract_text_from_images(image_paths, section_dir)

# Example usage
document_sections = [
    {
        'file_path': 'doc1.pdf',
        'sections': [
            {'title': 'Section A', 'start_page': 2, 'end_page': 5},
            {'title': 'Section B', 'start_page': 6, 'end_page': 10},
        ]
    },
    {
        'file_path': 'doc2.pdf',
        'sections': [
            {'title': 'Section A', 'start_page': 4, 'end_page': 8},
            {'title': 'Section C', 'start_page': 9, 'end_page': 12},
        ]
    },
    # Add more documents and sections as needed
]

output_base_path = 'output_sections'
extract_and_save_text(document_sections, output_base_path)
