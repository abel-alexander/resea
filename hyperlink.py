import fitz
import re
from typing import List, Dict

def extract_section_metadata_from_text(pdf_path: str, toc: List[List]) -> List[Dict]:
    """
    Enriches each TOC entry with:
    - page_count (based on next section's different start page)
    - title (boldest lines first, fallback to first 10 text lines, all joined with commas)
    - subtitle (line after title block)
    - creation_date (first date match from top 20 lines)
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched = []

    # Extended date regex supporting ordinal and common formats
    date_pattern = re.compile(
        r'(\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b|'     # 3rd August, 2025
        r'\b\w+\s\d{1,2}(st|nd|rd|th)?,\s+\d{4}\b|'        # August 3rd, 2025
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'              # 23/04/2024
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'                # 2024-04-23
        r'\b\w+\s\d{1,2},\s\d{4}\b|'                       # April 23, 2024
        r'\b\d{1,2}\s\w+\s\d{4}\b|'                        # 23 April 2024
        r'\b\w+\s\d{4}\b)',                                # April 2024
        re.IGNORECASE
    )

    for i, (level, section, start_page) in enumerate(toc):
        start_idx = start_page - 1

        # Compute page_count up to next different start_page
        end_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start > start_idx:
                end_idx = next_start - 1
                break
        page_count = max(1, end_idx - start_idx + 1)

        page = doc[start_idx]

        # ---- Collect lines from structured (span) text ----
        blocks = page.get_text("dict")["blocks"]
        span_lines = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                    font_size = line["spans"][0]["size"]
                    if len(line_text) > 3:
                        span_lines.append((line_text, font_size))

        # Use boldest spans (font size ≥ 80% of max)
        title_lines = []
        if span_lines:
            max_font = max(size for _, size in span_lines)
            threshold = max_font * 0.8
            title_lines = [text for text, size in span_lines if size >= threshold]

        # Fallback to markdown-style first 10 lines if needed
        if len(title_lines) < 3:
            text_lines = page.get_text("text").splitlines()
            text_lines = [line.strip() for line in text_lines if len(line.strip()) > 3]
            title_lines = text_lines[:10]

        title = ", ".join(title_lines)
        subtitle = text_lines[10] if len(text_lines) > 10 else ""

        # Detect first date in top 20 lines
        top_text = " ".join(text_lines[:20])
        date_match = date_pattern.search(top_text)
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
