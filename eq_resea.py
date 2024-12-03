import spacy

# Load SpaCy's medium-sized pre-trained model
nlp = spacy.load("en_core_web_md")

# Define the range of pages for "Equity Research"
equity_research_start = 250
equity_research_end = 300

# Define disclaimer patterns for each bank
disclaimer_patterns = {
    "JP Morgan": "J.P. Morgan does and seeks to do business with companies covered in its research reports",
    "BofA Securities": "ESGMeter is not indicative of company's future",
    "Morgan Stanley": "Morgan Stanley does and seeks to do business with companies",
}

# Threshold for semantic similarity (0.85 means 85% similar)
similarity_threshold = 0.85

# Initialize a dictionary to store results
bank_disclaimer_pages = {}

# Loop through the pages in the "Equity Research" section
for doc in pages:
    # Check if the page is within the given range
    if equity_research_start <= doc.metadata["page"] <= equity_research_end:
        # Preprocess the page content to handle multi-line text
        page_content = doc.page_content.replace("\n", " ").strip()

        # Convert the page content to a SpaCy document
        page_doc = nlp(page_content)

        # Check for each bank's disclaimer pattern in the preprocessed content
        for bank, pattern in disclaimer_patterns.items():
            # Convert the pattern to a SpaCy document
            pattern_doc = nlp(pattern)

            # Calculate semantic similarity
            similarity = page_doc.similarity(pattern_doc)

            # If the similarity exceeds the threshold, record the bank and page number
            if similarity > similarity_threshold:
                # Store the bank name and page number (only the first occurrence)
                if bank not in bank_disclaimer_pages:
                    bank_disclaimer_pages[bank] = doc.metadata["page"]

# Print the results
print(bank_disclaimer_pages)
