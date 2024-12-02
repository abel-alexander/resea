import io
import fitz  # PyMuPDF
from PIL import Image

# File path you want to extract images from
file = "1770.521236.pdf"

try:
    # Open the file
    pdf_file = fitz.open(file)

    # Iterate over PDF pages
    for page_index in range(len(pdf_file)):
        # Get the page itself
        page = pdf_file[page_index]
        image_list = page.getImageList()

        # Printing the number of images found on this page
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index + 1}")
        else:
            print(f"[!] No images found on page {page_index + 1}")

        for image_index, img in enumerate(image_list, start=1):
            # Get the XREF of the image
            xref = img[0]

            # Extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]

            # Get the image extension
            image_ext = base_image["ext"]

            # Load it to PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Save it to the local disk
            output_filename = f"image_page{page_index + 1}_img{image_index}.{image_ext}"
            image.save(output_filename)
            print(f"    [-] Saved image: {output_filename}")

    pdf_file.close()
    print("[+] Image extraction complete.")

except Exception as e:
    print(f"[!] Error: {e}")
