def should_skip_page(markdown_text: str, min_words: int = 30, min_table_lines: int = 3) -> bool:
    # Trim and check word count
    word_count = len(markdown_text.strip().split())
    if word_count < min_words:
        print(f"⏭️ Skipping: too short ({word_count} words)")
        return True

    # Check for table-like structure (at least N lines with numbers and 2+ tokens)
    tableish_lines = [
        line for line in markdown_text.splitlines()
        if any(char.isdigit() for char in line) and len(line.split()) >= 2
    ]
    if len(tableish_lines) < min_table_lines:
        print(f"⏭️ Skipping: not enough table-like lines ({len(tableish_lines)} found)")
        return True

    return False
