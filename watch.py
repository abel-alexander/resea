import fitz  # PyMuPDF

def pdf_get_toc(file_name):
    doc = fitz.open(file_name)
    toc = doc.get_toc(simple=True)  # Extract original ToC
    total_pages = doc.page_count

    # Check hyperlinks on page 1 and 2
    hyperlink_check = False
    for page_number in [0, 1]:  # Page 1 and 2 are 0-indexed
        page = doc[page_number]
        links = page.get_links()
        if len(links) > 3:  # More than 3 hyperlinks
            hyperlink_check = True
            break

    plst = []  # Initialize the output list
    if hyperlink_check:
        # New logic for pages with more than 3 hyperlinks
        toc_dict = {}
        for entry in toc:
            pno = entry[2]
            if pno > 0 and pno not in toc_dict:
                toc_dict[pno] = entry[1]

        section_counter = ord('A')  # Counter for unnamed sections
        id_counter = 1

        # Collect section data
        section_list = []  
        for pno in range(1, total_pages + 1):  # 1-indexed pages
            if pno in toc_dict:
                title = toc_dict[pno]
            else:
                page = doc[pno - 1]  # Convert to 0-indexed
                page_text = page.get_text("text").strip()
                if page_text:
                    title = page_text[:20].replace("\n", " ")
                else:
                    title = f"Section {chr(section_counter)}"
                    section_counter += 1
            section_list.append((id_counter, 1, title, pno))  # pno_from
            id_counter += 1

        # Now fix pno_to
        for i, (section_id, lvl, title, pno_from) in enumerate(section_list):
            if i < len(section_list) - 1:
                pno_to = section_list[i + 1][3] - 1  # One page before the next section
            else:
                pno_to = total_pages  # Last section goes till the end
            
            plst.append({
                "id": section_id,
                "lvl": lvl,
                "title": title,
                "pno_from": pno_from,
                "pno_to": pno_to,
            })

    else:
        # Original logic for ToC
