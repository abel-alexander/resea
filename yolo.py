import fitz
import re

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text("text")

    # Extract Table of Contents or fallback
    match = re.search(r"Table of Contents(.*)", first_page_text, re.DOTALL)
    if match:
        toc_text = match.group(1).strip()
    else:
        match = re.search(r"\b1\.\s*(.*)", first_page_text, re.DOTALL)
        if not match:
            return []
        toc_text = "1. " + match.group(1).strip()

    # Normalize and fix broken lines like "•\nTitle"
    toc_text = re.sub(r"([•\-])\n", r"\1 ", toc_text)
    lines = [line.strip() for line in toc_text.split("\n") if line.strip()]

    # Detect first marker to decide structure
    level1_marker = None
    for line in lines:
        if line.startswith("• "):
            level1_marker = "•"
            break
        elif line.startswith("- "):
            level1_marker = "-"
            break

    # Parse lines using detected structure
    toc_list = []
    for line in lines:
        if level1_marker == "•":
            if line.startswith("• "):
                level = 1
                section_name = line[2:].strip()
            elif line.startswith("- "):
                level = 2
                section_name = line[2:].strip()
            else:
                continue
        elif level1_marker == "-":
            if line.startswith("- "):
                level = 1
                section_name = line[2:].strip()
            elif line.startswith("• "):
                level = 2
                section_name = line[2:].strip()
            else:
                continue
        else:
            continue

        toc_list.append([level, section_name, None])

    # Extract page numbers from first-page links
    page_numbers = [
        int(link["page"]) + 1
        for link in doc[0].get_links()
        if "page" in link
    ]

    # Assign page numbers to TOC items
    page_index = 0
    for i in range(len(toc_list)):
        if toc_list[i][0] == 1:
            if page_index < len(page_numbers):
                toc_list[i][2] = page_numbers[page_index]
                page_index += 1
            if i + 1 < len(toc_list) and toc_list[i + 1][0] == 2:
                toc_list[i + 1][2] = toc_list[i][2]
        elif toc_list[i][0] == 2 and toc_list[i][2] is None:
            if page_index < len(page_numbers):
                toc_list[i][2] = page_numbers[page_index]
                page_index += 1

    return toc_list
