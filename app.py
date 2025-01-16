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

        # Iterate over all pages and extract ToC information
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

            # Append to plst with matching structure
            plst.append({
                "id": id_counter,
                "lvl": 1,
                "title": title,
                "pno_from": pno,
                "pno_to": pno,
            })
            id_counter += 1
    else:
        # Original logic for ToC
        last_lvl = 0
        nlvl = 0
        ntitle = ""
        npno_from = 0
        npno_to = 0
        id_counter = 1

        for i, item in enumerate(toc):
            lvl, title, pno = item
            for j, itemj in enumerate(toc):
                if j <= i or lvl >= 3:
                    continue

                if i == j:
                    nlvl = lvl
                    ntitle = title
                    npno_from = pno
                    npno_to = total_pages
                    if (id_counter + 1) == len(toc):
                        plst.append({
                            "id": id_counter,
                            "lvl": nlvl,
                            "title": ntitle,
                            "pno_from": npno_from,
                            "pno_to": npno_to,
                        })
                        id_counter += 1
                    break

                if j > i:
                    if lvl <= nlvl:
                        # Save the record
                        plst.append({
                            "id": id_counter,
                            "lvl": nlvl,
                            "title": ntitle,
                            "pno_from": npno_from,
                            "pno_to": npno_to,
                        })
                        id_counter += 1
                    break

    doc.close()
    return plst
