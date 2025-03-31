import fitz
import re
from typing import List, Dict

def extract_section_metadata_from_text(pdf_path: str, toc: List[List]) -> List[Dict]:
    """
    Enrich TOC entries with:
    - level, section, page_start (from TOC)
    - page_count (calculated from next section)
    - title (first line with 5+ words or 40+ chars from markdown-like text)
    - subtitle (next meaningful line)
    - creation_date (first matched date from top 20 lines)

    Returns a list of dicts with enriched metadata.
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched = []

    # Regex to detect one valid creation date only
    date_pattern = re.compile(
        r'(\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b|'     # 3rd August, 2025
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'             # 23/04/2024
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'               # 2024-04-23
        r'\b\w+\s\d{1,2},\s\d{4}\b|'                      # April 23, 2024
        r'\b\d{1,2}\s\w+\s\d{4}\b|'                       # 23 April 2024
        r'\b\w+\s\d{4}\b)',                               # April 2024
        re.IGNORECASE
    )

    for i, (level, section, start_page) in enumerate(toc):
        start_idx = start_page - 1
        end_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start >= start_idx:
                end_idx = max(start_idx, next_start - 1)
                break
        page_count = max(1, end_idx - start_idx + 1)

        page = doc[start_idx]
        text_lines = page.get_text("text").splitlines()
        text_lines = [line.strip() for line in text_lines if len(line.strip()) > 3]

        # Good title = first long line (5+ words or 40+ chars)
        title, subtitle = "", ""
        for idx, line in enumerate(text_lines):
            if len(line.split()) >= 5 or len(line) >= 40:
                title = line
                subtitle = text_lines[idx + 1] if idx + 1 < len(text_lines) else ""
                break
        if not title:
            title = text_lines[0] if text_lines else ""
            subtitle = text_lines[1] if len(text_lines) > 1 else ""

        # One-time creation_date detection only
        joined_text = " ".join(text_lines[:20])
        date_match = date_pattern.search(joined_text)
        creation_date = date_match.group(0) if date_match else ""

        enriched.append({
            "level": level,
            "section": section,
            "page_start": start_page,
            "page_count": page_count,
            "title": title,
            "subtitle": subtitle,
            "creation_date": creation_date
        })

    return enriched
import re

def enrich_answer_with_source_metadata(answer: str, enriched_sections: list) -> str:
    """
    Enriches a QA answer containing 'SourceRef: XYZ' with metadata:
    - section, page_start, page_count, title, creation_date

    Parameters:
    - answer (str): QA answer string with SourceRef
    - enriched_sections (list): Output from extract_section_metadata_from_text()

    Returns:
    - str: QA answer with inline metadata
    """
    match = re.search(r"SourceRef:\s*(.+)", answer)
    if not match:
        return answer

    raw_source = match.group(1).strip()
    clean_source = raw_source.replace("_", " ").lower()

    for section in enriched_sections:
        section_name = section.get("section", "").lower()
        if section_name in clean_source:
            meta = (
                f"(Section: {section.get('section', '')}, "
                f"Page Start: {section.get('page_start', '')}, "
                f"Page Count: {section.get('page_count', '')}, "
                f"Title: {section.get('title', '')}, "
                f"Date: {section.get('creation_date', '')})"
            )
            return answer.replace(match.group(0), f"{match.group(0)} {meta}")

    return answer  # fallback
