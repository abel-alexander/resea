from nltk.tag import StanfordNERTagger
import os
import re

# Set paths to Stanford NER model and jar file
stanford_classifier = "stanford_ner/classifiers/english.all.3class.distsim.crf.ser.gz"
stanford_ner_path = "stanford_ner/stanford-ner.jar"

# Initialize StanfordNERTagger
st = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding="utf-8")

def extract_companies_stanford(ocr_text):
    """Uses Stanford NER via NLTK to extract company names."""
    # Remove excessive newlines
    text = re.sub(r"\n+", " ", ocr_text).strip()

    # Tokenize text
    words = text.split()

    # Apply Stanford NER
    tagged_words = st.tag(words)

    # Extract company names
    company_names = [word for word, tag in tagged_words if tag == "ORGANIZATION"]

    return list(set(company_names))  # Remove duplicates

# Detect company names
company_names = extract_companies_stanford(ocr_text)

# Print extracted company names
print(company_names)
