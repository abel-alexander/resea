import fitz  # PyMuPDF
import re
from typing import List, Dict

def get_enhanced_section_metadata(pdf_path: str, toc: List[List]) -> List[Dict]:
    """
    Enrich TOC entries with:
      - page_start and page_count (based on next section's start)
      - bold_title: grouped lines from the top of the start page that have large font sizes (within 70% of the maximum)
      - subtitle: the first line after the title block
      - creation_date: a date extracted (from formats such as "23/04/2024", "2024-04-23", "April 23, 2024", "23 April 2024", or "April 2024")
    
    Parameters:
      pdf_path (str): Path to the PDF file.
      toc (List[List]): TOC entries in the format [level, section_title, start_page].
    
    Returns:
      List[Dict]: List of enriched metadata for each section.
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched_toc = []

    # Extended date regex pattern supporting multiple common formats.
    date_pattern = re.compile(
        r'(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'   # e.g., 23/04/2024 or 23-04-2024
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'       # e.g., 2024-04-23
        r'\b\w+\s\d{1,2},\s\d{4}\b|'              # e.g., April 23, 2024
        r'\b\d{1,2}\s\w+\s\d{4}\b|'               # e.g., 23 April 2024
        r'\b\w+\s\d{4}\b)'                       # e.g., April 2024
        r'\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b

        , re.IGNORECASE
    )

    for i, entry in enumerate(toc):
        level, section_title, start_page = entry
        start_page_idx = start_page - 1

        # Calculate page_count using next section's start (if any)
        end_page_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start_idx = toc[j][2] - 1
            if next_start_idx >= start_page_idx:
                end_page_idx = next_start_idx - 1
                break
        page_count = max(0, end_page_idx - start_page_idx + 1)

        # Extract all lines (text and corresponding font sizes) from the start page.
        page = doc[start_page_idx]
        blocks = page.get_text("dict")["blocks"]
        all_lines = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    spans = line["spans"]
                    if spans:
                        line_text = " ".join(span["text"] for span in spans).strip()
                        font_size = spans[0]["size"]
                        if line_text:
                            all_lines.append((line_text, font_size))

        # Determine the title block:
        bold_title = ""
        subtitle = ""
        if all_lines:
            max_font = max(size for _, size in all_lines)
            threshold = max_font * 0.7  # Accept lines with at least 70% of the maximum font size
            collected = []
            for idx, (text, size) in enumerate(all_lines):
                if size >= threshold:
                    collected.append(text)
                elif collected:
                    # The first line that doesn't meet the threshold after collecting title lines is taken as subtitle.
                    subtitle = text
                    break
            bold_title = " ".join(collected).strip()

        # Look for a date in the first 20 lines (or all if fewer)
        joined_top_lines = " ".join([text for text, _ in all_lines[:20]])
        date_match = date_pattern.search(joined_top_lines)
        creation_date = date_match.group(0) if date_match else ""

        enriched_toc.append({
            "section": section_title,
            "page_start": start_page,
            "page_count": page_count,
            "bold_title": bold_title,
            "subtitle": subtitle,
            "creation_date": creation_date
        })

    return enriched_toc

import re

def enrich_answer_with_source_metadata(answer: str, enriched_sections: list) -> str:
    """
    Enriches a QA answer ending with 'SourceRef: XYZ' by appending structured metadata:
    - section name
    - page_start
    - page_count
    - bold_title
    - creation_date (new!)

    Parameters:
    - answer (str): The QA answer string
    - enriched_sections (list): Output from get_enhanced_section_metadata()

    Returns:
    - str: Modified answer with metadata appended after SourceRef
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
                f"Title: {section['bold_title']}, "
                f"Date: {section.get('creation_date', '')})"
            )
            return answer.replace(match.group(0), f"{match.group(0)} {meta}")

    return answer  # fallback: unchanged
