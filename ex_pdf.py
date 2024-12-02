# Example list of document objects (replace with your actual data)
document_objects = [
    {"page_content": "Public Information Book\nPalantir Technologies Inc\nEarnings ReleasePublic Information Book", "metadata": {"source": "palantir.pdf", "page": 1}},
    {"page_content": "Earnings Transcript\nInvestor Presentation", "metadata": {"source": "palantir.pdf", "page": 2}},
    {"page_content": "10-K Annual Report\nDetails", "metadata": {"source": "palantir.pdf", "page": 3}},
    {"page_content": "Other Information", "metadata": {"source": "palantir.pdf", "page": 4}},
]

# Define the section keywords
section_keywords = ["Earnings Release", "Earnings Transcript", "10-K"]

# Initialize an empty dictionary to store results
sections = {}

# Loop through the document objects
for doc in document_objects:
    for keyword in section_keywords:
        # Check if the keyword exists in the page content
        if keyword in doc["page_content"]:
            # Add to dictionary with section name as key and page as value
            sections[keyword] = doc["metadata"]["page"]

# Print the dictionary
print(sections)
