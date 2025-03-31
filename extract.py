import fitz  # PyMuPDF
import re
from typing import List, Dict

def extract_section_metadata_from_text(pdf_path: str, toc: List[List]) -> List[Dict]:
    """
    For each TOC entry, extract:
    - start_page (from toc)
    - page_count (based on next toc entry)
    - title (first meaningful line)
    - subtitle (second line)
    - creation_date (from top 20 lines via regex)
    
    Parameters:
    - pdf_path (str): Path to the PDF
    - toc (List[List]): TOC entries like [level, section_name, start_page]
    
    Returns:
    - List[Dict]: Enriched metadata for each section
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched = []

    # Date pattern including formats like '3rd August, 2025'
    date_pattern = re.compile(
        r'(\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b|'             # 3rd August, 2025
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'                     # 23/04/2024 or 23-04-2024
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'                       # 2024-04-23
        r'\b\w+\s\d{1,2},\s\d{4}\b|'                              # April 23, 2024
        r'\b\d{1,2}\s\w+\s\d{4}\b|'                               # 23 April 2024
        r'\b\w+\s\d{4}\b)',                                       # April 2024
        re.IGNORECASE
    )

    for i, (level, section, start_page) in enumerate(toc):
        start_idx = start_page - 1
        end_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start >= start_idx:
                end_idx = next_start - 1
                break
        page_count = max(0, end_idx - start_idx + 1)

        # Extract plain text lines from start page
        page = doc[start_idx]
        lines = page.get_text("text").splitlines()
        lines = [line.strip() for line in lines if len(line.strip()) > 3]

        title = lines[0] if len(lines) > 0 else ""
        subtitle = lines[1] if len(lines) > 1 else ""

        # Extract creation date from top 20 lines
        text_top = " ".join(lines[:20])
        date_match = date_pattern.search(text_top)
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
    Detects 'SourceRef: XYZ' inside a QA answer and enriches it with metadata from matched section.
    
    New fields used:
    - page_start
    - page_count
    - title
    - creation_date

    Parameters:
    - answer (str): Full answer string with 'SourceRef: XYZ' line
    - enriched_sections (list): Output from extract_section_metadata_from_text()

    Returns:
    - str: Answer with enriched SourceRef metadata
    """
    match = re.search(r"SourceRef:\s*(.+)", answer)
    if not match:
        return answer  # No SourceRef found

    raw_source = match.group(1).strip()
    clean_source = raw_source.replace("_", " ").lower()

    for section in enriched_sections:
        section_name = section["section"].strip().lower()
        if section_name in clean_source:
            meta = (
                f"(Section: {section['section']}, "
                f"Page Start: {section['page_start']}, "
                f"Page Count: {section['page_count']}, "
                f"Title: {section['title']}, "
                f"Date: {section.get('creation_date', '')})"
            )
            return answer.replace(match.group(0), f"{match.group(0)} {meta}")

    return answer  # fallback: unchanged if no match
