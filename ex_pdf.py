# Initialize an empty dictionary to store results
sections = {}

# Loop through the `pages` list of Document objects
for doc in pages:
    # Check for occurrences of the pattern "{section}Public Information"
    if "Public Information" in doc.page_content:
        # Find the text before "Public Information"
        words = doc.page_content.split("Public Information")[0]
        # Get the keyword immediately preceding "Public Information"
        keyword = words.strip().split()[-1]
        if keyword:
            section_name = f"{keyword}Public Information"
            # Ignore page 0 and store the result
            if doc.metadata["page"] > 0:
                sections[section_name] = doc.metadata["page"]

# Print the dictionary
print(sections)
