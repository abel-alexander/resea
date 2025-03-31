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


import fitz  # PyMuPDF

def get_section_titles_with_page_counts(pdf_path: str, toc: list) -> list:
    """
    Works for all TOC levels: every entry gets its page_start, page_count, and bold title,
    even if multiple entries start on the same page.

    Parameters:
    - pdf_path (str): path to the PDF
    - toc (list): [[level, title, start_page], ...]

    Returns:
    - list of dicts with section, page_start, page_count, bold_title
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched_toc = []

    for i, entry in enumerate(toc):
        level, title, start_page = entry
        start_page_index = start_page - 1

        # Look for next TOC entry to determine page range
        end_page_index = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start_page = toc[j][2] - 1
            if next_start_page >= start_page_index:
                end_page_index = next_start_page - 1
                break

        page_count = max(0, end_page_index - start_page_index + 1)

        # Extract largest text from the start page
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


import fitz  # PyMuPDF
import re
from typing import List, Dict

def get_section_metadata_with_titles_and_dates(pdf_path: str, toc: List[List]) -> List[Dict]:
    """
    Enrich TOC entries with:
      - page range
      - bold title (largest font line or lines)
      - subtitle (line below title if available)
      - creation date (from top 8 lines)

    Parameters:
    - pdf_path (str): Path to the PDF file
    - toc (List[List]): List of [level, section_title, start_page]

    Returns:
    - List[Dict]: Each enriched TOC entry
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched_toc = []

    for i, entry in enumerate(toc):
        level, section_title, start_page = entry
        start_page_idx = start_page - 1

        # --- Calculate page_count ---
        end_page_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start >= start_page_idx:
                end_page_idx = next_start - 1
                break
        page_count = max(0, end_page_idx - start_page_idx + 1)

        # --- Analyze the start page ---
        page = doc[start_page_idx]
        blocks = page.get_text("dict")["blocks"]
        all_lines = []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                    if line_text:
                        all_lines.append((line_text, line["spans"][0]["size"]))

        # --- Bold title: collect all lines with max font size ---
        bold_title, subtitle = "", ""
        if all_lines:
            max_font = max(size for _, size in all_lines)
            bold_lines = [text for text, size in all_lines if size == max_font]
            bold_title = " ".join(bold_lines).strip()

            try:
                first_bold_idx = next(i for i, (text, size) in enumerate(all_lines) if size == max_font)
                if first_bold_idx + 1 < len(all_lines):
                    subtitle = all_lines[first_bold_idx + 1][0].strip()
            except StopIteration:
                subtitle = ""

        # --- Creation date detection (regex on top 8 lines) ---
        date_pattern = re.compile(
            r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'               # 01/02/2023 or 1-2-2023
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'                   # 2023-01-02
            r'\b\w+\s\d{1,2},\s\d{4}\b)',                         # April 24, 2024
            re.IGNORECASE
        )
        early_lines = " ".join([text for text, _ in all_lines[:8]])
        date_match = date_pattern.search(early_lines)
        creation_date = date_match.group(0) if date_match else ""

        # --- Append enriched section ---
        enriched_toc.append({
            "section": section_title,
            "page_start": start_page,
            "page_count": page_count,
            "bold_title": bold_title,
            "subtitle": subtitle,
            "creation_date": creation_date
        })

    return enriched_toc

