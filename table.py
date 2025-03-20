import fitz  # PyMuPDF
import re
import json

def extract_glossary(pdf_path):
    """Extracts glossary acronyms and their definitions."""
    glossary = {}
    doc = fitz.open(pdf_path)

    for page in doc:
        text = page.get_text("text")
        lines = text.split("\n")

        for line in lines:
            match = re.match(r"^([A-Z0-9&/]+)\s*–\s*(.+)$", line.strip())  # Detect "ACRONYM – Definition"
            if match:
                acronym, definition = match.groups()
                glossary[acronym] = definition.strip()

    return glossary

def extract_definition_chunks(pdf_path):
    """Extracts valuation framework text in smaller retrievable chunks."""
    doc = fitz.open(pdf_path)
    chunks = []

    for page in doc:
        text = page.get_text("text").strip()
        paragraphs = text.split("\n\n")  # Split by paragraphs

        for para in paragraphs:
            if len(para) > 100:  # Avoid very short lines
                chunks.append(para.strip())

    return chunks

# Paths to your PDFs
glossary_pdf_path = "glossary.pdf"
definition_pdf_path = "valuation_framework.pdf"

# Extract glossary acronyms
glossary_data = extract_glossary(glossary_pdf_path)
definition_chunks = extract_definition_chunks(definition_pdf_path)

# Save glossary as JSON
with open("glossary.json", "w") as f:
    json.dump(glossary_data, f, indent=4)

# Save definitions for later indexing
with open("definition_chunks.json", "w") as f:
    json.dump(definition_chunks, f, indent=4)

print("✅ Glossary and Definition File Extracted!")
