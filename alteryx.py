import fitz  # PyMuPDF
import re

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    # Extract text from the first page
    first_page_text = doc[0].get_text("text")

    # Extract everything after "Table of Contents"
    match = re.search(r"Table of Contents(.*)", first_page_text, re.DOTALL)
    if not match:
        return []  # No ToC found
    toc_text = match.group(1).strip()

    # Fix newline issue by merging lines properly
    toc_text = re.sub(r"(\d+\.|[ivxlc]+\.)\n", r"\1 ", toc_text, flags=re.IGNORECASE)

    # Split into lines and extract structure
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
            continue  # Skip unrelated text

        # Clean section name
        section_name = re.sub(r"^\d+\.", "", line).strip()  # Remove numbering
        section_name = re.sub(r"^[ivxlc]+\.", "", section_name, re.IGNORECASE).strip()  # Remove Roman numerals
        section_name = re.sub(r"\d{4}\.\d{2}\.\d{2}\s–", "", section_name).strip()  # Remove dates

        # Add to ToC list (page number to be mapped later)
        toc_list.append([level, section_name, None])

    # Extract page numbers from links on the first page
    first_page_links = doc[0].get_links()
    page_numbers = [int(link["page"]) + 1 for link in first_page_links if "page" in link]

    # Assign page numbers sequentially
    page_index = 0
    for i in range(len(toc_list)):
        if toc_list[i][0] == 1:  # Main section
            if page_index < len(page_numbers):
                toc_list[i][2] = page_numbers[page_index]  # Assign page number
                page_index += 1  # Move to the next page number
            
            # Ensure the first sub-item inherits the same page number
            if i + 1 < len(toc_list) and toc_list[i + 1][0] == 2:
                toc_list[i + 1][2] = toc_list[i][2]  # Inherit parent’s page number
        elif toc_list[i][0] == 2 and toc_list[i][2] is None:  
            # Only assign a new page number if it's not inherited
            if page_index < len(page_numbers):
                toc_list[i][2] = page_numbers[page_index]
                page_index += 1  # Move to next page number

    return toc_list

# Example usage
pdf_path = "your_file.pdf"
toc_output = extract_toc_from_pdf(pdf_path)

# Print structured output
for item in toc_output:
    print(item)  # Example: [1, 'Recent Earnings Material', 3]
