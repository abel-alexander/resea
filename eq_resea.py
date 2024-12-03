from fuzzywuzzy import fuzz

# Define the range of pages for "Equity Research"
equity_research_start = 250
equity_research_end = 300

# Define disclaimer patterns for each bank
disclaimer_patterns = {
    "JP Morgan": "J.P. Morgan does and seeks to do business with companies covered in its research reports",
    "BofA Securities": "ESGMeter is not indicative of company's future",
    "Morgan Stanley": "Morgan Stanley does and seeks to do business with companies",
}

# Threshold for fuzzy matching
fuzzy_threshold = 80

# Initialize a dictionary to store results
bank_disclaimer_pages = {}

# Loop through the pages in the "Equity Research" section
for doc in pages:
    # Check if the page is within the given range
    if equity_research_start <= doc.metadata["page"] <= equity_research_end:
        # Preprocess the page content to handle multi-line text
        page_content = doc.page_content.replace("\n", " ").strip()

        # Check for each bank's disclaimer pattern in the preprocessed content
        for bank, pattern in disclaimer_patterns.items():
            # Use fuzzy matching to compare the pattern and page content
            similarity = fuzz.partial_ratio(pattern, page_content)

            if similarity > fuzzy_threshold:
                # Store the bank name and page number (only the first occurrence)
                if bank not in bank_disclaimer_pages:
                    bank_disclaimer_pages[bank] = doc.metadata["page"]

# Print the results
print(bank_disclaimer_pages)
