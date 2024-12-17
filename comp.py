import re
import pytesseract
from PIL import Image
import fitz  # PyMuPDF for PDFs

def extract_toc_from_images(image_files):
    """
    Extract the Table of Contents (TOC) from image files using OCR.
    Args:
        image_files (list): List of image file paths.
    Returns:
        list: Cleaned TOC entries with titles and hyperlinks.
    """
    toc_entries = []

    for image_path in image_files:
        # Perform OCR on the image
        text = pytesseract.image_to_string(Image.open(image_path))

        # Identify Table of Contents section using regex
        if "Table of Contents" in text:
            print(f"\nTOC Found in: {image_path}")
            # Extract lines under Table of Contents
            lines = text.split("\n")
            for line in lines:
                # Match entries like "1. Title Page" or "3. Subsection"
                match = re.match(r"(\d+)\.\s+(.+)", line)
                if match:
                    page, title = match.groups()
                    toc_entries.append({"Title": title.strip(), "Page": int(page)})

    return toc_entries


def extract_toc_from_pdf(pdf_path):
    """
    Extract hyperlinks from PDFs and fetch the TOC.
    Args:
        pdf_path (str): Path to the PDF.
    Returns:
        list: TOC entries with titles and target pages.
    """
    toc_entries = []
    pdf = fitz.open(pdf_path)
    
    for page_num, page in enumerate(pdf, start=1):
        links = page.get_links()  # Extract hyperlinks from each page
        text = page.get_text("text")

        # Check for Table of Contents
        if "Table of Contents" in text:
            print(f"TOC Found on Page {page_num}")
            lines = text.split("\n")
            for line in lines:
                # Match TOC format (e.g., 1. Title, Hyperlinked)
                match = re.match(r"(\d+)\.\s+(.+)", line)
                if match:
                    page_ref, title = match.groups()
                    target_page = None

                    # Look for hyperlink pointing to the target page
                    for link in links:
                        if "page" in link and link["page"] == int(page_ref):
                            target_page = link["page"] + 1  # PDF pages start at 0
                            break
                    
                    toc_entries.append({"Title": title.strip(), "Target Page": target_page})
    
    pdf.close()
    return toc_entries


def format_clean_toc(toc_entries):
    """
    Clean and format TOC entries into a readable format.
    Args:
        toc_entries (list): List of TOC entries.
    """
    print("\nClean Table of Contents:")
    for entry in toc_entries:
        print(f"- {entry['Title']} (Page: {entry.get('Target Page', 'N/A')})")


# === Usage ===
# For images:
image_files = ["image1.jpeg", "image2.jpeg", "image3.jpeg", "image4.jpeg"]  # Replace with paths
toc_from_images = extract_toc_from_images(image_files)
format_clean_toc(toc_from_images)

# For PDFs:
pdf_path = "sample.pdf"  # Replace with your PDF file path
toc_from_pdf = extract_toc_from_pdf(pdf_path)
format_clean_toc(toc_from_pdf)
