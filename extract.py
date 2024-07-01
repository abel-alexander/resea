import fitz  # PyMuPDF
import easyocr
import os

# Function to extract images from PDF and apply OCR using EasyOCR
def extract_images_and_text(pdf_path):
    # Create a directory to save images
    if not os.path.exists("pdf_images"):
        os.makedirs("pdf_images")

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    image_counter = 1
    reader = easyocr.Reader(['en'])

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        # Get images on the page
        images = page.get_images(full=True)
        for image_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_extension = base_image["ext"]
            image_path = f"pdf_images/page{page_number + 1}_img{image_index + 1}.{image_extension}"

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            
            # Perform OCR on the image using EasyOCR
            text = reader.readtext(image_path, detail=0)
            print(f"Text from image {image_path}:")
            print(' '.join(text))
            print("-" * 50)

# Example usage
pdf_path = "path_to_your_pdf.pdf"
extract_images_and_text(pdf_path)
