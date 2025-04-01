import fitz
import re

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text("text")

    # Extract ToC or fallback
    match = re.search(r"Table of Contents(.*)", first_page_text, re.DOTALL)
    if match:
        toc_text = match.group(1).strip()
    else:
        match = re.search(r"\b1\.\s*(.*)", first_page_text, re.DOTALL)
        if not match:
            return []
        toc_text = "1. " + match.group(1).strip()

    # Normalize bullets and dashes
    toc_text = toc_text.replace("•", "[BULLET]").replace("–", "[HYPHEN]").replace("-", "[HYPHEN]")

    # Fix broken lines
    toc_text = re.sub(r"(\d+\.|[ivxlc]+\.|[a-zA-Z][\.\)]|\[BULLET\]|\[HYPHEN\])\n", r"\1 ", toc_text, flags=re.IGNORECASE)

    toc_list = []
    last_level = None

    for line in toc_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect structure
        if line.startswith("[BULLET]"):
            level = 1
        elif line.startswith("[HYPHEN]"):
            level = 2 if last_level == 1 else 1  # use context
        elif re.match(r"^\d+\.", line):
            level = 1
        elif re.match(r"^[a-zA-Z][\.\)]", line):
            level = 2
        else:
            continue

        last_level = level

        # Clean up prefix
        section_name = re.sub(r"^(\[BULLET\]|\[HYPHEN\]|\d+\.\s*|[a-zA-Z][\.\)]\s*)", "", line, flags=re.IGNORECASE).strip()
        toc_list.append([level, section_name, None])

    # Page number mapping
    first_page_links = doc[0].get_links()
    page_numbers = [int(link["page"]) + 1 for link in first_page_links if "page" in link]

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
