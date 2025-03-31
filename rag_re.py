import fitz  # PyMuPDF

def get_section_titles_with_page_counts(pdf_path: str, toc: list) -> list:
    """
    Extracts enriched TOC metadata from a PDF:
    - section title
    - start page
    - page count (based on next section's start page)
    - boldest text from the section's first page (largest font)

    Parameters:
    - pdf_path (str): Path to the PDF file
    - toc (list): List of [level, title, start_page]

    Returns:
    - List[dict]: Each section's metadata
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched_toc = []

    for i, entry in enumerate(toc):
        level, title, start_page = entry
        start_page_index = start_page - 1
        end_page_index = toc[i + 1][2] - 2 if i + 1 < len(toc) else num_pages - 1
        page_count = end_page_index - start_page_index + 1

        # Extract boldest (largest font) text from the start page
        page = doc[start_page_index]
        blocks = page.get_text("dict")["blocks"]
        max_font_size = 0
        bold_title = ""

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    size = span.get("size", 0)
                    text = span.get("text", "").strip()
                    if size > max_font_size and len(text) > 5:
                        max_font_size = size
                        bold_title = text

        enriched_toc.append({
            "section": title,
            "page_start": start_page,
            "page_count": page_count,
            "bold_title": bold_title
        })

    return enriched_toc
import re

def enrich_answer_with_source_metadata(answer: str, enriched_sections: list) -> str:
    """
    Enriches a QA answer that ends with 'SourceRef: XYZ' by appending metadata:
    - page_start
    - page_count
    - bold_title

    Parameters:
    - answer (str): The answer string with a SourceRef line
    - enriched_sections (list): Output from get_section_titles_with_page_counts

    Returns:
    - str: Modified answer with metadata inline after the SourceRef
    """
    match = re.search(r"SourceRef:\s*(.+)", answer)
    if not match:
        return answer  # no SourceRef found

    raw_source = match.group(1).strip()
    clean_source = raw_source.replace("_", " ").lower()

    for section in enriched_sections:
        section_name = section["section"].strip().lower()
        if section_name in clean_source:
            # Create and append metadata
            meta = (
                f"(Section: {section['section']}, "
                f"Page Start: {section['page_start']}, "
                f"Page Count: {section['page_count']}, "
                f"Title: {section['bold_title']})"
            )
            return answer.replace(match.group(0), f"{match.group(0)} {meta}")

    return answer  # no match found
toc = [
    [1, "Equity Research", 5],
    [1, "Valuation", 11],
    [1, "Risks", 15]
]

pdf_path = "pib1.pdf"
enriched_sections = get_section_titles_with_page_counts(pdf_path, toc)

qa_answer = "The company's EPS trends are improving.\n\nSourceRef: Equity_Research_abc"
enriched = enrich_answer_with_source_metadata(qa_answer, enriched_sections)
print(enriched)
