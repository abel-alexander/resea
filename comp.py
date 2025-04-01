import fitz
import re
from typing import List, Dict, Callable

def extract_section_metadata_llm_title(pdf_path: str, toc: List[List], llm_pipeline: Callable) -> List[Dict]:
    """
    Uses an LLM to extract a clean section title from the start page.
    Uses regex to extract the creation/publication date from top 20 lines.
    Computes page_count by looking ahead to the next different start page.

    Parameters:
    - pdf_path: path to PDF
    - toc: list of [level, section, page_start]
    - llm_pipeline: HuggingFace text-generation pipeline

    Returns:
    - List of dicts: level, section, page_start, page_count, title, creation_date
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched = []

    # Date regex (strict)
    date_pattern = re.compile(
        r'('
        r'\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b|'     # 3rd August, 2025
        r'\b\w+\s\d{1,2}(st|nd|rd|th)?,\s+\d{4}\b|'       # August 3rd, 2025
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'             # 23/04/2024
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'               # 2024-04-23
        r'\b\w+\s\d{1,2},\s\d{4}\b|'                      # April 23, 2024
        r'\b\d{1,2}\s\w+\s\d{4}\b'                        # 23 April 2024
        r')',
        re.IGNORECASE
    )

    for i, (level, section, start_page) in enumerate(toc):
        start_idx = start_page - 1

        # Compute page_count using next different start page
        end_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start > start_idx:
                end_idx = next_start - 1
                break
        page_count = max(1, end_idx - start_idx + 1)

        # Get page text
        page = doc[start_idx]
        page_text = page.get_text("text").strip()

        # LLM prompt
        prompt = (
            "From the page text below, extract the most important title or heading "
            "that best summarizes the section. Respond with:\n\nTitle: ...\n\n"
            f"---\n{page_text}"
        )

        # Call LLM
        try:
            output = llm_pipeline(prompt, max_new_tokens=128, temperature=0.75, do_sample=False)
            result = output[0]['generated_text']
        except Exception as e:
            print(f"[ERROR] LLM failed for section '{section}' (page {start_page}): {e}")
            result = ""

        # Parse title from LLM output
        title = ""
        for line in result.splitlines():
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[-1].strip()

        # Regex date from top 20 lines
        lines = page_text.splitlines()
        lines = [line.strip() for line in lines if len(line.strip()) > 3]
        top_text = " ".join(lines[:20])
        top_text = re.sub(r"\s+", " ", top_text).strip()

        date_match = date_pattern.search(top_text)
        creation_date = date_match.group(0) if date_match else ""

        enriched.append({
            "level": level,
            "section": section,
            "page_start": start_page,
            "page_count": page_count,
            "title": title,
            "creation_date": creation_date
        })

    return enriched
