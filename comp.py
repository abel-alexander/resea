import re
from typing import List, Dict

def extract_section_metadata_from_markdown(md_text: str, toc: List[List]) -> List[Dict]:
    """
    Extract section metadata from a markdown string using TOC info.
    
    Parameters:
    - md_text: Full markdown text as a string (from .md file)
    - toc: List of [level, section_title, start_page]
    
    Returns:
    - List of dicts with section metadata: title, subtitle, page_count, creation_date
    """
    # Split markdown into pages based on metadata-inferred page numbers
    pages = md_text.split("\n\nPage ")  # assumes "Page X" exists at start or inline
    page_map = {}
    for page_block in pages:
        lines = page_block.strip().splitlines()
        if not lines:
            continue
        first_line = lines[0]
        match = re.match(r"(?:Page\s+)?(\d+)", first_line)
        if match:
            page_num = int(match.group(1))
            page_map[page_num] = lines

    enriched = []

    # Date pattern supporting many formats including "3rd August, 2025"
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
        end_page = toc[i + 1][2] - 1 if i + 1 < len(toc) else max(page_map.keys())
        page_count = max(1, end_page - start_page + 1)

        lines = page_map.get(start_page, [])
        lines = [line.strip() for line in lines if len(line.strip()) > 3]

        # Title = first long or meaningful line
        title, subtitle = "", ""
        for idx, line in enumerate(lines[:20]):
            if len(line.split()) >= 5 or len(line) >= 40:
                title = line
                if idx + 1 < len(lines):
                    subtitle = lines[idx + 1]
                break
        if not title:
            title = lines[0] if lines else ""
            subtitle = lines[1] if len(lines) > 1 else ""

        # Creation date: only first match
        joined_top = " ".join(lines[:20])
        match = date_pattern.search(joined_top)
        creation_date = match.group(0) if match else ""

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
