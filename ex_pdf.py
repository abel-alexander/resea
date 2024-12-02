# Initialize an empty dictionary to store results
sections = {}

# Loop through the `pages` list of Document objects
for doc in pages:
    # Check for occurrences of "Public Information"
    if "Public Information" in doc.page_content:
        # Split the content to isolate the text before "Public Information"
        split_content = doc.page_content.split("Public Information")[0]
        # Ensure there's text before "Public Information"
        if split_content.strip():
            # Extract the keyword immediately preceding "Public Information"
            keyword = split_content.strip().split()[-1] if split_content.strip().split() else None
            if keyword:  # Only proceed if a keyword is found
                section_name = f"{keyword}Public Information"
                # Ignore page 0 and store the result
                if doc.metadata["page"] > 0:
                    sections[section_name] = doc.metadata["page"]

# Print the dictionary
print(sections)
