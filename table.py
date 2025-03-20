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

# Extract and save glossary
glossary_pdf_path = "glossary.pdf"
glossary_data = extract_glossary(glossary_pdf_path)

# Save as JSON for fast retrieval
with open("glossary.json", "w") as f:
    json.dump(glossary_data, f, indent=4)

print("✅ Glossary extracted and saved!")
