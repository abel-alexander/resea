import fitz  # PyMuPDF
import re

# Predefined Level 2 section list
section_list = ["Earnings Report", "Earnings Transcript", "Research", "Equity Research", "Earnings Call"]

def get_level1_from_toc(pdf_path):
    """Extract Level 1 titles from the default PDF ToC, ignoring irrelevant pages."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    
    # Remove any Level 1 sections that come from irrelevant pages (like '0.0 PIB Cover')
    valid_level1_sections = [entry[1] for entry in toc if entry[0] == 1 and not entry[1].lower().startswith(("0.0", "cover", "public information book"))]

    return valid_level1_sections

def clean_text(ocr_text):
    """Cleans OCR text while preserving structure (avoiding early newline removal)."""
    match = re.search(r"Table of Contents(.*)", ocr_text, re.DOTALL)
    if not match:
        return ""  # No valid text found
    text = match.group(1).strip()

    # Remove unwanted text (logos, artifacts)
    text = re.sub(r"Zz.*?ZH", "", text, flags=re.DOTALL | re.IGNORECASE)  # Remove OCR logo artifacts
    text = re.sub(r"[^a-zA-Z0-9\s.\n-]", "", text)  # Remove non-alphanumeric artifacts

    # Preserve single newlines but remove excessive ones
    text = re.sub(r"\n{2,}", "\n", text).strip()  # Remove excessive empty lines but keep structure

    return text

def extract_toc_hybrid(pdf_path, ocr_text):
    """Uses PDF ToC + OCR text to extract structured sections."""
    level1_sections = get_level1_from_toc(pdf_path)  # Get valid Level 1s
    cleaned_text = clean_text(ocr_text)

    lines = cleaned_text.split("\n")
    toc_list = []
    current_level1 = None
    level1_index = 0  # Track Level 1 sections

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # If it's in section_list, assign it as Level 2 under current Level 1
        if line in section_list:
            if current_level1:  # Ensure Level 1 is assigned before adding Level 2
                toc_list.append([2, line, None])  # Assign as Level 2 under current Level 1
        
        # If it's not in section_list, treat it as a new Level 1
        elif level1_index < len(level1_sections):
            current_level1 = level1_sections[level1_index]  # Assign new Level 1
            toc_list.append([1, current_level1, None])  
            level1_index += 1  # Move to next Level 1

    return toc_list

