# Define the specific section keywords to look for
section_keywords = ["Earnings Release", "Earnings Call", "10-K", "Equity Research", "Recent News"]

# Initialize an empty dictionary to store results
sections = {}

# Loop through the `pages` list of Document objects
for doc in pages:
    # Loop through the known section keywords
    for keyword in section_keywords:
        # Look for the pattern "{section}Public Information" in the page content
        search_pattern = f"{keyword}Public Information"
        if search_pattern in doc.page_content:
            # Ignore page 0 and store the result
            if doc.metadata["page"] > 0:
                sections[search_pattern] = doc.metadata["page"]

# Print the dictionary
print(sections)
