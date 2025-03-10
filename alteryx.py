import fitz  # PyMuPDF
import re

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    # Extract text from the first page only
    first_page = doc[0].get_text("text")

    # Keep only text after "Table of Contents"
    match = re.search(r"Table of Contents(.*)", first_page, re.DOTALL)
    if not match:
        return []  # Return empty list if no ToC found
    toc_text = match.group(1).strip()  # Extract text after "Table of Contents"

    # Split into lines and process ToC structure
    toc_list = []
    for line in toc_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Determine hierarchy level (1 = main, 2 = sub-section)
        if re.match(r"^\d+\.", line):  # Level 1 (e.g., "1. Recent Earnings")
            level = 1
        elif re.match(r"^[ivxlc]+\.", line, re.IGNORECASE):  # Level 2 (e.g., "i. Q1 2024")
            level = 2
        else:
            continue  # Skip unstructured text

        # Clean section name
        section_name = re.sub(r"^\d+\.|\bi\b\.|\bii\b\.|\biii\b\.|\biv\b\.", "", line).strip()

        # Add entry (page number to be filled later)
        toc_list.append([level, section_name, None])

    # Extract links from the first page only
    link_map = {}  # {section_name: page_number}
    first_page_links = doc[0].get_links()  # Extract only from first page

    for link in first_page_links:
        if "page" in link:
            page_number = int(link["page"]) + 1  # Convert to 1-based index
            rect = link.get("from", None)
            if rect:
                # Extract text in link area to map section to page
                link_text = doc[0].get_textbox(rect).strip()
                link_map[link_text] = page_number  # Store as integer

    # Assign page numbers
    for entry in toc_list:
        section = entry[1]
        if section in link_map:
            entry[2] = link_map[section]  # Assign correct page number

    return toc_list

# Example usage
pdf_path = "your_file.pdf"
toc_output = extract_toc_from_pdf(pdf_path)

# Print structured output
for item in toc_output:
    print(item)  # Example: [1, 'Recent Earnings Material', 2]
