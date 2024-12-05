import fitz  # PyMuPDF


def convert_pdf_to_images_with_fit(pdf_path, output_folder="output_images"):
    """Convert PDF pages to images using PyMuPDF."""
    import os
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)  # Render the page at 300 DPI
        output_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(output_path)
        image_paths.append(output_path)

    return image_paths


# Example usage
pdf_path = "pib1.pdf"
images = convert_pdf_to_images_with_fit(pdf_path)
print(f"Saved images: {images}")
