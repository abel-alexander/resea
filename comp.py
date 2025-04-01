import fitz
import re
from PIL import Image
import pytesseract
from typing import List, Dict, Callable

def extract_section_metadata_ocr_llm_title(pdf_path: str, toc: List[List], llm_pipeline: Callable) -> List[Dict]:
    """
    Uses OCR + LLM to extract the title from the first page of each section.
    Uses regex to extract creation date from the OCR text.
    Calculates page_count from TOC entries.

    Parameters:
    - pdf_path: path to the PDF
    - toc: list of [level, section, start_page]
    - llm_pipeline: HuggingFace text-generation pipeline

    Returns:
    - List of dicts with metadata per section
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    enriched = []

    # Date pattern for real dates (not 'Q1 2024')
    date_pattern = re.compile(
        r'('
        r'\b\d{1,2}(st|nd|rd|th)?\s+\w+,\s+\d{4}\b|'     
        r'\b\w+\s\d{1,2}(st|nd|rd|th)?,\s+\d{4}\b|'       
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|'             
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b|'               
        r'\b\w+\s\d{1,2},\s\d{4}\b|'                      
        r'\b\d{1,2}\s\w+\s\d{4}\b'                        
        r')',
        re.IGNORECASE
    )

    for i, (level, section, start_page) in enumerate(toc):
        start_idx = start_page - 1
        page = doc[start_idx]

        # --- OCR step ---
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ocr_text = pytesseract.image_to_string(img)
        ocr_lines = [line.strip() for line in ocr_text.splitlines() if len(line.strip()) > 3]

        # Use OCR output in LLM prompt
        prompt = (
            "You are helping identify a meaningful section title from the start page of a company document.\n\n"
            "From the following page text, extract a concise, human-readable title that best summarizes the section.\n\n"
            "- If there is an explicit report name or heading (e.g. 'Back in Black - Reiterate OW'), use it.\n"
            "- If it's a regulatory document like 'Form 6-K', use that and any company name near it.\n"
            "- Ignore metadata, disclaimers, and footnotes.\n\n"
            "Respond only in this format:\n\n"
            "Title: <clean title>\n\n"
            f"---\n{ocr_text}"
        )

        try:
            output = llm_pipeline(prompt, max_new_tokens=128, temperature=0.75, do_sample=False)
            result = output[0]['generated_text']
        except Exception as e:
            print(f"[ERROR] LLM failed for section '{section}' (page {start_page}): {e}")
            result = ""

        # Parse title from LLM result
        title = ""
        for line in result.splitlines():
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[-1].strip()

        # Regex search for date from OCR text
        top_text = " ".join(ocr_lines[:20])
        top_text = re.sub(r"\s+", " ", top_text).strip()
        date_match = date_pattern.search(top_text)
        creation_date = date_match.group(0) if date_match else ""

        # Compute page_count
        end_idx = num_pages - 1
        for j in range(i + 1, len(toc)):
            next_start = toc[j][2] - 1
            if next_start > start_idx:
                end_idx = next_start - 1
                break
        page_count = max(1, end_idx - start_idx + 1)

        enriched.append({
            "level": level,
            "section": section,
            "page_start": start_page,
            "page_count": page_count,
            "title": title,
            "creation_date": creation_date
        })

    return enriched
