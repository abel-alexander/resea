import fitz  # PyMuPDF

def pdf_get_toc(file_name, max_title_length=50):
    doc = fitz.open(file_name)
    toc = doc.get_toc(simple=True)  # Extract original ToC
    total_pages = doc.page_count

    # Extract hyperlinks from page 3 (ToC page)
    toc_page_number = 2  # 3rd page (0-based index)
    toc_page = doc[toc_page_number]
    links = toc_page.get_links()

    # Collect linked pages
    linked_pages = set()
    for link in links:
        if "page" in link and link["page"] is not None:
            linked_pages.add(link["page"] + 1)  # Convert to 1-indexed

    # If more than 3 hyperlinks exist, process them
    hyperlink_check = len(linked_pages) > 3

    plst = []  # Final output list
    if hyperlink_check:
        print("Inside hybrid ToC logic")

        # Create a ToC lookup dictionary {page_number: title}
        toc_dict = {entry[2]: entry[1] for entry in toc if entry[2] > 0}

        section_counter = ord('A')  # For fallback sections (A, B, C, ...)
        id_counter = 1
        section_list = []

        # Process only hyperlinked pages
        for pno in sorted(linked_pages):
            if pno in toc_dict and toc_dict[pno].strip():  # If valid title exists
                title = toc_dict[pno]
                # ✅ Shorten long titles
                if len(title) > max_title_length:
                    title = title[:max_title_length] + "..."
            else:
                # Assign a generic unknown section instead of extracting text
                title = f"Unknown Section {chr(section_counter)}"
                section_counter += 1

            section_list.append((id_counter, 1, title, pno))
            id_counter += 1

        print(section_list)

        # Fix `pno_to`
        for i, (section_id, lvl, title, pno_from) in enumerate(section_list):
            if i < len(section_list) - 1:
                pno_to = section_list[i + 1][3] - 1  # One page before next section
            else:
                pno_to = total_pages  # Last section spans till the end

            plst.append({
                "id": section_id,
                "lvl": lvl,
                "title": title,
                "pno_from": pno_from,
                "pno_to": pno_to,
            })

    else:
        # Process standard ToC if hyperlinks aren't useful
        toc_sorted = sorted(toc, key=lambda x: x[2])  # Sort by page number
        id_counter = 1

        for i, (lvl, title, pno_from) in enumerate(toc_sorted):
            if lvl >= 3:  # Ignore deep nested levels
                continue

            # ✅ Shorten long titles
            if len(title) > max_title_length:
                title = title[:max_title_length] + "..."

            if i < len(toc_sorted) - 1:
                pno_to = toc_sorted[i + 1][2] - 1
            else:
                pno_to = total_pages

            plst.append({
                "id": id_counter,
                "lvl": lvl,
                "title": title,
                "pno_from": pno_from,
                "pno_to": pno_to,
            })
            id_counter += 1

    doc.close()

    # Print the extracted Table of Contents
    for entry in plst:
        print(entry)

    return plst  # Return the structured ToC as a list of dictionaries
