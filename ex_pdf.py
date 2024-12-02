# Define the specific section keywords to look for
section_keywords = ["Earnings Release", "Earnings Call", "10-K", "Equity Research", "Recent News"]

# Initialize an empty dictionary to store results
sections = {}

# Loop through the `pages` list of Document objects
for doc in pages:
    # Loop through the known section keywords
    for keyword in section_keywords:
        # Look for the pattern "{section}Public Information" in the page content
        search_pattern = f"{keyword}Public Information"
        if search_pattern in doc.page_content:
            # Ignore page 0 and store the result
            if doc.metadata["page"] > 0:
                sections[search_pattern] = doc.metadata["page"]

# Print the dictionary
print(sections)



import fitz  # PyMuPDF
from PIL import Image
import io

# Define the PDF file and the page range
pdf_path = "palantir.pdf"
start_page = 250  # Starting page
end_page = 300    # Ending page

# Output directory for the images
output_dir = "./extracted_images/"

# Open the PDF file
doc = fitz.open(pdf_path)

# Loop through the specified page range
for page_num in range(start_page - 1, end_page):  # PyMuPDF uses 0-based indexing
    page = doc.load_page(page_num)
    images = page.get_images(full=True)  # Get all images on the page

    for i, img in enumerate(images):
        xref = img[0]  # Reference to the image object
        base_image = doc.extract_image(xref)  # Extract the image
        image_bytes = base_image["image"]  # Get the image data as bytes
        image_ext = base_image["ext"]  # Get the image format (e.g., png, jpeg)

        # Create an image from the bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save the image
        image.save(f"{output_dir}page_{page_num + 1}_image_{i + 1}.{image_ext}")

print("Image extraction completed.")
