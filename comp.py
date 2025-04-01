from typing import List, Dict, Callable
import fitz  # PyMuPDF

def extract_title_date_llm(pdf_path: str, toc: List[List], llm_pipeline: Callable) -> List[Dict]:
    """
    For each section in the TOC, extract the start page's text and use an LLM
    to extract a clean section title and creation date.

    Parameters:
    - pdf_path: path to the PDF file
    - toc: List of [level, section_title, start_page]
    - llm_pipeline: a HuggingFace text-generation pipeline

    Returns:
    - List of dicts with: level, section, page_start, title, creation_date
    """
    doc = fitz.open(pdf_path)
    enriched = []

    for level, section, start_page in toc:
        page_idx = start_page - 1
        page_text = doc[page_idx].get_text("text").strip()

        # Prompt for the LLM
        prompt = (
            "You are helping extract metadata from the first page of a document section.\n\n"
            "From the text below, extract:\n"
            "1. A clean section title (concise and readable)\n"
            "2. A clearly formatted creation or publication date (if found)\n\n"
            "Respond in this format:\n"
            "Title: ...\n"
            "Date: ...\n\n"
            f"---\n{page_text}"
        )

        try:
            result = llm_pipeline(prompt, max_new_tokens=128)[0]['generated_text']
        except Exception as e:
            print(f"[ERROR] LLM failed for section '{section}' (page {start_page}): {e}")
            result = ""

        # Parse LLM output
        title, date = "", ""
        for line in result.splitlines():
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("date:"):
                date = line.split(":", 1)[-1].strip()

        enriched.append({
            "level": level,
            "section": section,
            "page_start": start_page,
            "title": title,
            "creation_date": date
        })

    return enriched
