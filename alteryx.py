import fitz  # PyMuPDF

def extract_hyperlinked_toc(doc):
    """
    Extracts a Table of Contents (ToC) from a PDF by detecting hyperlinks and matching them with actual ToC entries.
    If no match is found, it assigns 'Unknown Section from page: pno_from to page: pno_to'.
    """
    plst = []  # Final structured output
    unique_entries = set()  # To prevent duplicates
    id_counter = 1

    # Step 1: Check pages 1 → 2 → 3 for many hyperlinks
    selected_page = None
    for page_num in range(3):
        page = doc[page_num]
        links = page.get_links()
        if len(links) > 3:
            selected_page = page_num
            break

    if selected_page is None:
        print("No page with more than 3 hyperlinks found. No ToC generated.")
        return []

    print(f"Using Page {selected_page + 1} for ToC extraction.")

    # Step 2: Extract all hyperlinks and target pages
    selected_page_obj = doc[selected_page]
    links = selected_page_obj.get_links()

    # Extract inbuilt ToC as a lookup dictionary
    toc_dict = {entry[2]: entry[1] for entry in doc.get_toc(simple=True) if entry[2] > 0}

    temp_list = []  # Temporary list to store entries before sorting

    for link in links:
        destination_page = link.get("page", -1) + 1  # Convert to 1-indexed
    
        if destination_page <= 1:  
            continue  # Ignore links pointing to page 1 or invalid links
    
        # Step 3: Match the page with actual ToC
        matched_text = toc_dict.get(destination_page, None)
    
        # Step 4: If no match, name it as "Unknown Section from page: pno_from to page: pno_to"
        if not matched_text:
            matched_text = f"Unknown Section from page: {destination_page} to page: ?"
    
        # Avoid duplicates
        entry_key = (matched_text, destination_page)
        if entry_key in unique_entries:
            continue
        unique_entries.add(entry_key)
    
        # Store in temp_list (without ID yet)
        temp_list.append({
            "lvl": 1,
            "title": matched_text,
            "pno_from": destination_page,
            "pno_to": destination_page  # Will adjust later
        })
    
    # Step 5: Sort by `pno_from` before assigning IDs
    plst = sorted(temp_list, key=lambda x: x["pno_from"])
    
    # Assign correct sequential IDs
    for idx, entry in enumerate(plst, start=1):
        entry["id"] = idx  # Ensures correct ordering
    
    # Ensure `pno_to` follows hyperlink order
    for i in range(len(plst) - 1):
        plst[i]["pno_to"] = plst[i + 1]["pno_from"] - 1  # Assign next section's start - 1
    
    # Ensure the last section spans till the last page
    if plst:
        plst[-1]["pno_to"] = doc.page_count


    return plst

# Example usage in a Jupyter Notebook
pdf_path = "pib1.pdf"
doc = fitz.open(pdf_path)
toc = extract_hyperlinked_toc(doc)

# Print the extracted ToC
for entry in toc:
    print(f"{entry['id']}. {entry['title']} (Pages {entry['pno_from']}-{entry['pno_to']})")
