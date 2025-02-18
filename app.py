import fitz  # PyMuPDF

def pdf_get_toc_with_links(file_name):
    doc = fitz.open(file_name)
    toc_page_number = 2  # 3rd page (0-based index)
    toc_page = doc[toc_page_number]

    # Extract hyperlinks and text blocks from the ToC page
    links = toc_page.get_links()
    text_blocks = toc_page.get_text("blocks")

    plst = []  # Final output list
    unique_entries = set()  # To prevent duplicates

    section_counter = ord('A')  # Counter for unknown sections
    id_counter = 1

    for link in links:
        link_rect = fitz.Rect(link["from"])  # Get the hyperlink bounding box
        destination_page = link["page"] + 1  # Convert to 1-indexed

        # Expand bounding box slightly to capture surrounding text
        expanded_rect = link_rect + (-5, -2, 5, 2)

        matched_text = None
        min_distance = float("inf")

        # Iterate over text blocks to find the closest match
        for block in text_blocks:
            text_rect = fitz.Rect(block[:4])  # Get text bounding box
            if expanded_rect.intersects(text_rect):  # Check if expanded box intersects
                # Select the closest text block
                distance = abs(link_rect.y0 - text_rect.y0)
                if distance < min_distance:
                    matched_text = block[4].strip()
                    min_distance = distance

        # Assign a fallback name if no match is found
        if not matched_text:
            matched_text = f"Unknown Section {chr(section_counter)}"
            section_counter += 1

        # Avoid duplicates
        entry_key = (matched_text, destination_page)
        if entry_key in unique_entries:
            continue  # Skip duplicate entries
        unique_entries.add(entry_key)

        # Append result in plst format
        plst.append({
            "id": id_counter,
            "lvl": 1,
            "title": matched_text,
            "pno_from": destination_page,
            "pno_to": destination_page  # We will adjust this later
        })
        id_counter += 1

    # Fix pno_to to correctly span across pages
    for i in range(len(plst)):
        if i < len(plst) - 1:
            plst[i]["pno_to"] = plst[i + 1]["pno_from"] - 1
        else:
            plst[i]["pno_to"] = doc.page_count  # Last entry spans till the end

    doc.close()

    # Print the final structured ToC
    for entry in plst:
        print(entry)

    return plst
