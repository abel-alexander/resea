import fitz  # PyMuPDF
import re

def get_level1_from_toc(pdf_path):
    """Extract Level 1 titles from the default PDF ToC."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    level1_sections = [entry[1] for entry in toc if entry[0] == 1]  # Extract only Level 1
    return level1_sections

def clean_text(ocr_text):
    """Cleans OCR text by removing unwanted sections and normalizing spacing."""
    match = re.search(r"Table of Contents(.*)", ocr_text, re.DOTALL)
    if not match:
        return ""  # No valid text found
    text = match.group(1).strip()

    # Remove unwanted text (logos, artifacts)
    text = re.sub(r"BofA SECURITIES.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^a-zA-Z0-9\s.\n-]", "", text)  # Remove unusual characters
    text = re.sub(r"\n+", "\n", text).strip()  # Normalize spacing
    
    return text

def extract_toc_hybrid(pdf_path, ocr_text):
    """Uses PDF ToC + OCR text to extract structured sections."""
    level1_sections = get_level1_from_toc(pdf_path)  # Get valid Level 1s
    cleaned_text = clean_text(ocr_text)

    lines = cleaned_text.split("\n")
    toc_list = []
    current_level1 = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this extracted item is a substring of a Level 1 section in get_toc()
        matched_level1 = next((toc_name for toc_name in level1_sections if line in toc_name), None)

        if matched_level1:
            current_level1 = matched_level1
            toc_list.append([1, current_level1, None])  # Use full name from get_toc()
        elif current_level1:
            # Anything after Level 1 is Level 2
            toc_list.append([2, line, None])

    return toc_list



# Extract structured ToC
toc_output = extract_toc_hybrid(pdf_path, ocr_text)

# Print structured output
for item in toc_output:
    print(item)  # Example: [1, 'Birkenstock Holding plc', None]  [2, 'Earnings Report', None]
