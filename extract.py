import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import PyPDF2

# Path to the PDF file
pdf_path = 'your_pdf_file.pdf'

# Directory to save images
image_dir = 'pdf_images'
os.makedirs(image_dir, exist_ok=True)

# Define the page range to extract (e.g., pages 440 to 444)
start_page = 440
end_page = 444

# Convert specific pages of PDF to images
images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
image_paths = []

for i, image in enumerate(images):
    page_number = start_page + i
    image_path = os.path.join(image_dir, f'page_{page_number}.png')
    image.save(image_path, 'PNG')
    image_paths.append(image_path)

# Extract text from images using pytesseract
extracted_texts = []

for i, image_path in enumerate(image_paths):
    text = pytesseract.image_to_string(Image.open(image_path))
    extracted_texts.append({
        'page_number': start_page + i,
        'image_path': image_path,
        'text': text
    })

# Combine all extracted text into a single string (for convenience)
full_text = "\n".join([entry['text'] for entry in extracted_texts])

# Print the extracted text
print(full_text)

# Optionally, save the extracted text and metadata to a file
with open('extracted_text_with_metadata.txt', 'w') as text_file:
    for entry in extracted_texts:
        text_file.write(f"Page {entry['page_number']} (Image: {entry['image_path']}):\n")
        text_file.write(entry['text'])
        text_file.write("\n" + "-"*80 + "\n")

# Extract PDF metadata using PyPDF2
with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfFileReader(file)
    pdf_metadata = reader.getDocumentInfo()

# Print PDF metadata
for key, value in pdf_metadata.items():
    print(f'{key}: {value}')

# Optionally, save PDF metadata to a file
with open('pdf_metadata.txt', 'w') as meta_file:
    for key, value in pdf_metadata.items():
        meta_file.write(f'{key}: {value}\n')





import fitz  # PyMuPDF
from PIL import Image

def convert_pdf_to_images(pdf_path, pages, output_folder):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    for page_num in pages:
        # Ensure the page number is within the PDF
        if page_num < 0 or page_num >= pdf_document.page_count:
            print(f"Page number {page_num} is out of range")
            continue

        # Select the page
        page = pdf_document.load_page(page_num)
        
        # Render the page to a pixmap
        pix = page.get_pixmap()
        
        # Convert to PIL Image
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save the image
        image_path = f"{output_folder}/page_{page_num + 1}.png"
        image.save(image_path)
        print(f"Page {page_num + 1} saved as {image_path}")

# Example usage
pdf_path = 'your_pdf_file.pdf'
pages = [0, 2, 4]  # page numbers to convert (0-indexed)
output_folder = 'output_images'

convert_pdf_to_images(pdf_path, pages, output_folder)

