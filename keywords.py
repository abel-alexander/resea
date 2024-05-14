import pdfplumber
import pandas as pd
from collections import Counter
import re


def extract_company_sections(pdf_path):
    sections = []
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # Assuming each company section starts with "Company Report" and ends before the next starts
        parts = full_text.split("Company Report")[1:]  # Skip the first split before the first header
        for part in parts:
            end = part.find("End of Company Report")  # Each section ends with this text
            sections.append(part[:end])
    return sections


def count_keywords(text, keywords):
    words = re.findall(r'\b\w+\b', text.lower())
    counter = Counter(words)
    return {keyword: counter.get(keyword, 0) for keyword in keywords}


def process_pdf(pdf_path, keywords):
    sections = extract_company_sections(pdf_path)
    results = []
    for section in sections:
        keyword_counts = count_keywords(section, keywords)
        results.append(keyword_counts)
    return results


# Define your keywords
keywords = ["investment", "market", "growth", "risk", "profit"]

# Paths to your PDFs
pdf_paths = ["pib1.pdf"]#, "pib2.pdf", "pib3.pdf", "pib4.pdf", "pib5.pdf", "pib6.pdf"]

for index, path in enumerate(pdf_paths):
    results = process_pdf(path, keywords)
    with pd.ExcelWriter(f"{path[:-4]}_keyword_frequency.xlsx") as writer:
        for i, result in enumerate(results):
            df = pd.DataFrame([result])
            df.index = [f"Company {i + 1}"]
            df.to_excel(writer, sheet_name=f"Company {i + 1}")

        # Concatenate all results for summary sheet
        concatenated_df = pd.concat([pd.DataFrame([res]) for res in results], ignore_index=True)
        concatenated_df.to_excel(writer, sheet_name="Concatenated Summary")

