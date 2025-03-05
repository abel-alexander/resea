import fitz  # PyMuPDF for PDF processing
import re
import pytesseract
from pdf2image import convert_from_path
import numpy as np

def extract_hyperlinks(pdf_path, toc_pages=[0, 1, 2]):
    """Extracts hyperlinks and their corresponding target pages from the ToC pages."""
    doc = fitz.open(pdf_path)
    links = []

    for page_num in toc_pages:
        if page_num < len(doc):
            page = doc[page_num]
            for link in page.get_links():
                if "page" in link:
                    links.append(link["page"])  # Only take internal page links

    doc.close()
    return sorted(set(links))  # Return unique page numbers in order

def extract_toc_text_ocr(pdf_path, toc_pages=[0, 1, 2]):
    """Extracts text from the ToC pages using OCR (pytesseract)."""
    images = convert_from_path(pdf_path, first_page=min(toc_pages), last_page=max(toc_pages) + 1)
    text_data = [pytesseract.image_to_string(img) for img in images]
    return "\n".join(text_data)  # Combine extracted text from multiple pages

def parse_toc_structure(toc_text):
    """
    Parses ToC structure by detecting numbering patterns (e.g., 1, 2, 3... or i, ii, iii...).
    - Handles nested numbering like 1.1, 1.2, 2.1.1
    """
    lines = toc_text.split("\n")
    toc_entries = []

    for line in lines:
        line = line.strip()
        match = re.match(r"(\d+[\.\d+]*)\s+(.*)", line)  # Detects numbers with possible sub-numbers (1.1, 2.3.1)
        if match:
            toc_entries.append((match.group(1), match.group(2)))  # (Section Number, Section Name)

    return toc_entries  # Returns structured list of (section_number, section_name)

def map_hyperlinks_to_toc(toc_entries, hyperlink_pages):
    """Maps extracted hyperlinks to the ToC sections following top-to-bottom order."""
    if len(hyperlink_pages) < len(toc_entries):
        print("Warning: More ToC entries than hyperlinks! Some sections may be missing links.")

    mapped_toc = []
    for i, (section_number, section_name) in enumerate(toc_entries):
        target_page = hyperlink_pages[i] if i < len(hyperlink_pages) else None  # Avoid index errors
        mapped_toc.append((section_number, section_name, target_page))

    return mapped_toc  # Returns structured list with mapped pages

def refine_toc_with_llm(mapped_toc):
    """Refines the mapped ToC using an LLM to improve structure and readability."""
    toc_input = "\n".join([f"{sec_num}. {sec_name} → Page {page}" for sec_num, sec_name, page in mapped_toc])

    prompt = f"""
    You are an expert in structuring a Table of Contents.
    Here is an extracted Table of Contents with page mappings:
    
    {toc_input}
    
    Ensure the structure follows correct hierarchy, keeping indentation or numbering style intact.
    - Maintain sections and subsections properly.
    - Make sure the page mappings follow the top-to-bottom order.
    
    Refined Table of Contents:
    """

    response = llm(prompt, max_length=10000)  # Adjust for your LLM
    return response

# **Final Execution Flow**
pdf_path = "your_file.pdf"  # Change to your PDF file
toc_pages = [0, 1, 2]  # Adjust based on where the ToC is in the document

# Step 1: Extract hyperlinks from the ToC pages
hyperlinks = extract_hyperlinks(pdf_path, toc_pages)

# Step 2: Extract ToC text via OCR
toc_text = extract_toc_text_ocr(pdf_path, toc_pages)

# Step 3: Parse ToC structure
toc_entries = parse_toc_structure(toc_text)

# Step 4: Map hyperlinks to extracted ToC entries
mapped_toc = map_hyperlinks_to_toc(toc_entries, hyperlinks)

# Step 5: Pass to LLM for refinement
refined_toc = refine_toc_with_llm(mapped_toc)

# Output
print(refined_toc)
