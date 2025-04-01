import fitz  # PyMuPDF
import re

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text("text")

    # Try extracting after "Table of Contents"
    match = re.search(r"Table of Contents(.*)", first_page_text, re.DOTALL)
    if match:
        toc_text = match.group(1).strip()
    else:
        # Fallback: Look for first item like '1. Title' even if broken by newline
        match = re.search(r"\b1\.\s*(.*)", first_page_text, re.DOTALL)
        if not match:
            return []  # No match at all
        toc_text = "1. " + match.group(1).strip()

    # Normalize bullets and dashes
    toc_text = toc_text.replace("•", "-").replace("–", "-")

    # Fix broken lines like: "a)\nTitle" → "a) Title"
    toc_text = re.sub(r"(\d+\.|[ivxlc]+\.|[a-zA-Z][\.\)]|-)\n", r"\1 ", toc_text, flags=re.IGNORECASE)

    toc_list = []
    for line in toc_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect hierarchy
        if re.match(r"^\d+\.", line):  # "1. Title"
            level = 1
        elif re.match(r"^([a-zA-Z][\.\)])", line):  # "a) Title"
            level = 2
        elif re.match(r"^- ", line):  # "- Title"
            level = 2
        else:
            # Heuristic fallback: assume capitalized top-level titles
            if len(line) > 8 and line == line.title():
                level = 1
            else:
                continue

        # Clean up prefix (number, bullet, etc.)
        section_name = re.sub(r"^(\d+\.\s*|[ivxlc]+\.\s*|[a-zA-Z][\.\)]\s*|- )", "", line, flags=re.IGNORECASE).strip()
        toc_list.append([level, section_name, None])

    # Get links for page numbers
    first_page_links = doc[0].get_links()
    page_numbers = [int(link["page"]) + 1 for link in first_page_links if "page" in link]

    # Assign page numbers
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
