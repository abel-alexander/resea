from typing import List, Dict, Callable
import fitz  # PyMuPDF

def extract_title_date_llm(pdf_path: str, toc: List[List], llm_pipeline: Callable) -> List[Dict]:
    """
    Uses LLM to extract clean title and creation date from the start page of each TOC entry.
    
    Parameters:
    - pdf_path: path to PDF
    - toc: list of [level, section, page_start]
    - llm_pipeline: HuggingFace text-generation pipeline (no generate_kwargs)

    Returns:
    - List of dicts with extracted metadata
    """
    doc = fitz.open(pdf_path)
    enriched = []

    for level, section, start_page in toc:
        page_idx = start_page - 1
        page_text = doc[page_idx].get_text("text").strip()

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
            output = llm_pipeline(prompt, max_new_tokens=128, temperature=0.75, do_sample=False)
            result = output[0]['generated_text']
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
