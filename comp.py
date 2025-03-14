import nltk
import re
from nltk import word_tokenize, pos_tag, ne_chunk

# Download necessary NLTK models (Run this once)
nltk.download("punkt")
nltk.download("maxent_ne_chunker")
nltk.download("words")

def extract_companies_nltk(ocr_text):
    """Uses NLTK's NER chunking to extract company names (ORG entities)."""
    # Remove excessive newlines
    text = re.sub(r"\n+", " ", ocr_text).strip()

    # Tokenize & POS tagging
    words = word_tokenize(text)
    pos_tags = pos_tag(words)

    # Named entity recognition
    named_entities = ne_chunk(pos_tags)

    # Extract company names (ORG labels)
    company_names = []
    for chunk in named_entities:
        if hasattr(chunk, "label") and chunk.label() == "ORGANIZATION":
            company_names.append(" ".join(c[0] for c in chunk))

    return list(set(company_names))  # Remove duplicates

# Example OCR text
ocr_text = """
Public Information Book March 2024 Table of Contents
Birkenstock 6. Nike Earnings Report Earnings Transcript Research
Deckers 7. On Holding Earnings Report Earnings Transcript Research
Levi Strauss & Skechers Earnings Report Earnings Transcript Research
Lululemon Earnings Report Earnings Transcript Research
VF Corp Earnings Report Earnings Transcript Research
Moncler Earnings Report Earnings Transcript Research
"""

# Detect company names
company_names = extract_companies_nltk(ocr_text)

# Print extracted company names
print(company_names)
