import fitz  # PyMuPDF

def get_page_numbers_from_links(pdf_path, toc_page):
    """Extracts page numbers from hyperlinks on the ToC page."""
    doc = fitz.open(pdf_path)
    links = doc[toc_page].get_links()
    
    # Extract page numbers from valid links
    page_numbers = sorted([int(link["page"]) + 1 for link in links if "page" in link])  # Convert to 1-based indexing

    print("\n🔹 Extracted Page Numbers from Links:", page_numbers)  # Debugging
    return page_numbers

def assign_page_numbers(toc_list, page_numbers):
    """Assigns page numbers to Level 1 and Level 2 sections correctly."""
    page_index = 0  # Tracks which page number to assign

    for i in range(len(toc_list)):
        if toc_list[i][0] == 1:  # If it's a Level 1 section
            if page_index < len(page_numbers):  # Ensure page number exists
                toc_list[i][2] = page_numbers[page_index]  # Assign page number
                parent_page = page_numbers[page_index]  # Store for Level 2
                page_index += 1  # Move to the next page number
            
        elif toc_list[i][0] == 2:  # If it's a Level 2 section
            toc_list[i][2] = parent_page  # Inherit page number from Level 1

    print("\n✅ Final Structured ToC with Page Numbers:")
    for item in toc_list:
        print(item)  # Debug output
    
    return toc_list


pdf_path = "sd.pdf"
toc_page = 0  # Assuming the ToC is on the first page

# Extract structured ToC
toc_list = extract_toc_hybrid(pdf_path, ocr_text)

# Get page numbers from hyperlinks
page_numbers = get_page_numbers_from_links(pdf_path, toc_page)

# Assign page numbers to ToC entries
final_toc = assign_page_numbers(toc_list, page_numbers)
