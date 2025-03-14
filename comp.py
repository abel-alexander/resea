import re
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk

# Ensure necessary NLTK data is downloaded
nltk.download("punkt")
nltk.download("maxent_ne_chunker")
nltk.download("words")

def clean_text(ocr_text):
    """Removes unwanted sections and extracts only relevant content."""
    # Keep only text after "Table of Contents"
    match = re.search(r"Table of Contents(.*)", ocr_text, re.DOTALL)
    if not match:
        return ""  # No valid text found
    text = match.group(1).strip()

    # Remove unwanted logo-based text (e.g., "BofA SECURITIES")
    text = re.sub(r"BofA SECURITIES.*", "", text, flags=re.IGNORECASE)

    # Remove section names ("Earnings Report", "Earnings Transcript", "Research")
    sections_to_remove = ["Earnings Report", "Earnings Transcript", "Research"]
    for section in sections_to_remove:
        text = re.sub(rf"\b{section}\b", "", text, flags=re.IGNORECASE)

    # Remove excessive whitespace and newlines
    text = re.sub(r"\n+", " ", text).strip()
    
    return text

def extract_companies_nltk(cleaned_text):
    """Uses NLTK's NER chunking to extract company names while preserving order."""
    words = word_tokenize(cleaned_text)
    pos_tags = pos_tag(words)
    named_entities = ne_chunk(pos_tags)

    company_names = []
    for chunk in named_entities:
        if hasattr(chunk, "label") and chunk.label() == "ORGANIZATION":
            company_names.append(" ".join(c[0] for c in chunk))

    return company_names  # Maintain order

# Example OCR text
ocr_text = """
Public Information Book March 2024 Table of Contents
Birkenstock 6. Nike Earnings Report Earnings Transcript Research
Deckers 7. On Holding Earnings Report Earnings Transcript Research
Levi Strauss & Skechers Earnings Report Earnings Transcript Research
Lululemon Earnings Report Earnings Transcript Research
VF Corp Earnings Report Earnings Transcript Research
Moncler Earnings Report Earnings Transcript Research
BofA SECURITIES zh Nike
"""

# Clean and extract company names
cleaned_text = clean_text(ocr_text)
company_names = extract_companies_nltk(cleaned_text)

# Print extracted company names
print(company_names)
