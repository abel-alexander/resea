import fitz
import re
from typing import List, Dict

def extract_section_metadata_from_text(pdf_path: str, toc: List[List]) -> List[Dict]:
    """
    For each TOC entry, enrich with:
    - level, section, page_start (from TOC)
    - page_count (up to next different start_page in TOC)
    - title: joined first 10 non-trivial lines from start page
    - subtitle: 11th line if available
    - creation_date: first matched date from top 20 lines
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched = []

    # Match dates like "23rd April, 2024", "April 23rd, 2024", "23/04/2024", etc.
    date_pattern = re.compile(
        r'(\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b|'   # 3rd August, 2025
        r'\b\w+\s\d{1,2}(st|nd|rd|th)?,\s+\d{4}\b|'      # August 3rd, 2025
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'            # 23/04/2024
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'              # 2024-04-23
        r'\b\w+\s\d{1,2},\s\d{4}\b|'                     # April 23, 2024
        r'\b\d{1,2}\s\w+\s\d{4}\b|'                      # 23 April 2024
        r'\b\w+\s\d{4}\b)',                              # April 2024
        re.IGNORECASE
    )

    for i, (level, section, start_page) in enumerate(toc):
        start_idx = start_page - 1

        # Find end of this section: next different start_page
        end_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start > start_idx:
                end_idx = next_start - 1
                break

        page_count = max(1, end_idx - start_idx + 1)

        # Extract text lines from the page
        page = doc[start_idx]
        lines = page.get_text("text").splitlines()
        lines = [line.strip() for line in lines if len(line.strip()) > 3]

        # Title: first 10 good lines joined with commas
        title_lines = lines[:10]
        title = ", ".join(title_lines)
        subtitle = lines[10] if len(lines) > 10 else ""

        # Detect date from top 20 lines only
        joined_text = " ".join(lines[:20])
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
    Enriches a QA answer that ends with 'SourceRef: XYZ' using metadata.
    Adds section name, page info, title, creation_date.

    Parameters:
    - answer: QA answer string
    - enriched_sections: list of dicts from extract_section_metadata_from_text()

    Returns:
    - Enriched answer with metadata inline after SourceRef
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

    return answer
# Step 1: Define your TOC and PDF path
toc = [
    [1, "Wall Street Research", 1091],
    [2, "2024.04.23 - UBS Equities", 1091],
    [2, "2024.04.23 - Wells Fargo Securities", 1181],
]
pdf_path = "pib1.pdf"

# Step 2: Extract enriched section data
enriched_sections = extract_section_metadata_from_text(pdf_path, toc)

# Step 3: Enrich a QA answer with SourceRef
qa = "EPS beat expected due to margin growth.\nSourceRef: UBS Equities"
print(enrich_answer_with_source_metadata(qa, enriched_sections))
