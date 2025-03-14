import re
import collections

def clean_text(ocr_text):
    """Removes unwanted sections and extracts only relevant content."""
    # Keep only text after "Table of Contents"
    match = re.search(r"Table of Contents(.*)", ocr_text, re.DOTALL)
    if not match:
        return ""  # No valid text found
    text = match.group(1).strip()

    # Remove unwanted text from logos (e.g., "BofA SECURITIES")
    text = re.sub(r"BofA SECURITIES.*", "", text, flags=re.IGNORECASE)

    # Remove non-text artifacts (e.g., unwanted symbols, extra spaces)
    text = re.sub(r"[^a-zA-Z0-9\s.\n-]", "", text)

    # Normalize spacing
    text = re.sub(r"\n+", "\n", text).strip()
    
    return text

def extract_toc_structure(cleaned_text):
    """Extracts companies as Level 1 and assigns repeating subsections as Level 2 dynamically."""
    lines = cleaned_text.split("\n")
    toc_list = []
    level_1_sections = []  # Store unique company names
    level_2_counts = collections.Counter()  # Count occurrences of each potential subsection

    # First pass: Identify unique company names and count repeating subsections
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r"^\d+\.", line):  # Detect Level 1 (company names)
            section_name = re.sub(r"^\d+\.", "", line).strip()
            level_1_sections.append(section_name)
        else:
            level_2_counts[line] += 1  # Count occurrences of potential subsections

    # Identify the most common subsection names (they repeat for multiple companies)
    subsection_threshold = len(level_1_sections) // 2  # Subsections must appear in at least 50% of companies
    level_2_sections = {sec for sec, count in level_2_counts.items() if count >= subsection_threshold}

    # Second pass: Assign sections correctly
    level_1_index = 1
    for company in level_1_sections:
        toc_list.append([1, company, None])  # Add company as Level 1

        for subsection in level_2_sections:  # Assign detected subsections under each company
            toc_list.append([2, subsection, None])

    return toc_list



# Clean and extract structured ToC
cleaned_text = clean_text(ocr_text)
toc_output = extract_toc_structure(cleaned_text)

# Print structured ToC output
for item in toc_output:
    print(item)  # Example: [1, 'Birkenstock', None]  [2, 'Earnings Report', None]
