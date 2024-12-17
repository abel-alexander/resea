def identify_toc_entries(lines):
    """
    Identify Level 1 and Level 2 entries and preserve hierarchy.
    Args:
        lines (list): List of lines from OCR text.
    Returns:
        dict: Structured TOC with Level 1 as keys and Level 2 as child entries.
    """
    toc_structure = {}
    current_level1 = None

    # Regex patterns
    level1_pattern = r"^\d+\.\s"  # Matches Level 1 (e.g., '1. Recent Earnings')
    level2_pattern = r"^\s*[ivxlc]+\.\s"  # Matches Level 2 (e.g., 'i. Q1 2024...')

    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        # Check for Level 1
        if re.match(level1_pattern, line):
            current_level1 = line
            toc_structure[current_level1] = []
        # Check for Level 2 under the current Level 1
        elif current_level1 and re.match(level2_pattern, line):
            toc_structure[current_level1].append(line.strip())

    return toc_structure
