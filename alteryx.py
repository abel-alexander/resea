import fitz  # PyMuPDF

def pdf_recreate_toc(file_name):
    doc = fitz.open(file_name)
    first_page = doc[0]  # Extract from the first page
    links = first_page.get_links()
    text_blocks = first_page.get_text("blocks")  # Extract text blocks

    plst = []  # Final output list
    unique_entries = set()  # Prevent duplicate entries
    section_counter = ord('A')  # For unknown sections
    id_counter = 1

    # Extract inbuilt ToC as a fallback
    toc_dict = {entry[2]: entry[1] for entry in doc.get_toc(simple=True) if entry[2] > 0}

    for link in links:
        if "page" in link and isinstance(link["page"], int):
            destination_page = link["page"] + 1  # Convert to 1-indexed
        else:
            continue  # Skip invalid links

        link_rect = fitz.Rect(link["from"])  # Hyperlink bounding box
        expanded_rect = link_rect + (-5, -2, 5, 2)  # Expand for better text capture

        matched_text = None
        min_distance = float("inf")

        # Find the closest text block overlapping the link
        for block in text_blocks:
            text_rect = fitz.Rect(block[:4])
            if expanded_rect.intersects(text_rect):
                distance = abs(link_rect.y0 - text_rect.y0)
                if distance < min_distance:
                    matched_text = block[4].strip()
                    min_distance = distance

        # Use inbuilt ToC as a fallback if no matched text found
        if not matched_text:
            matched_text = toc_dict.get(destination_page, f"Unknown Section {chr(section_counter)}")
            section_counter += 1 if "Unknown Section" in matched_text else 0

        # Avoid duplicates
        entry_key = (matched_text, destination_page)
        if entry_key in unique_entries:
            continue
        unique_entries.add(entry_key)

        # Append to plst
        plst.append({
            "id": id_counter,
            "lvl": 1,
            "title": matched_text,
            "pno_from": destination_page,
            "pno_to": destination_page  # Will adjust later
        })
        id_counter += 1

    # Adjust `pno_to` correctly
    for i in range(len(plst)):
        if i < len(plst) - 1:
            plst[i]["pno_to"] = plst[i + 1]["pno_from"] - 1
        else:
            plst[i]["pno_to"] = doc.page_count  # Last section spans till the end

    doc.close()

    # Print structured ToC
    for entry in plst:
        print(entry)

    return plst
