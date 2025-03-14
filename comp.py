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

    # Remove any text between 'Zz' and 'ZH' (dynamic logo detection)
    text = re.sub(r"Zz.*?ZH", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove non-alphanumeric artifacts (e.g., unwanted symbols)
    text = re.sub(r"[^a-zA-Z0-9\s.\n-]", "", text)  
    text = re.sub(r"\n+", "\n", text).strip()  # Normalize spacing

    # Handle broken numbering (e.g., missing numbers before company names)
    text = re.sub(r"\n\n?\(", "\n", text)  # Remove weird newline artifacts before company names

    return text

def extract_toc_hybrid(pdf_path, ocr_text):
    """Uses PDF ToC + OCR text to extract structured sections."""
    level1_sections = get_level1_from_toc(pdf_path)  # Get valid Level 1s
    cleaned_text = clean_text(ocr_text)

    lines = cleaned_text.split("\n")
    toc_list = []
    current_level1 = None

    # Normalize level 1 names for easier matching
    level1_normalized = {name.lower().strip(): name for name in level1_sections}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Handle companies that may not have a number (e.g., "Nike" instead of "6. Nike")
        line_cleaned = re.sub(r"^\d+\.\s*", "", line).strip()  # Remove leading numbers

        # Check if this extracted item matches a Level 1 name from get_toc()
        matched_level1 = next((full_name for norm_name, full_name in level1_normalized.items() if line_cleaned.lower() in norm_name), None)

        if matched_level1:
            current_level1 = matched_level1
            toc_list.append([1, current_level1, None])  # Use full name from get_toc()
        elif current_level1:
            # Anything after Level 1 is Level 2
            toc_list.append([2, line, None])

    return toc_list

# Example usage
pdf_path = "aprl.pdf"
ocr_text = """
Public Information Book March 2024 Table of Contents
1. Birkenstock
Earnings Report
Earnings Transcript
Research
2. Deckers
Earnings Report
Earnings Transcript
Research
3. Levi Strauss
Earnings Report
Earnings Transcript
Research
4. Lululemon
Earnings Report
Earnings Transcript
Research
5. Moncler
Earnings Report
Earnings Transcript
Research
Nike
Earnings Report
Earnings Transcript
Research
Zz BofA SECURITIES ZH
On Holding
Earnings Report
Earnings Transcript
Research
Skechers
Earnings Report
Earnings Transcript
Research
VF Corp
Earnings Report
Earnings Transcript
Research
"""

# Extract structured ToC
toc_output = extract_toc_hybrid(pdf_path, ocr_text)

# Print structured output
for item in toc_output:
    print(item)  # Example: [1, 'Nike, Inc. Class B', None]  [2, 'Earnings Report', None]
