# Function to standardize and extract years
def extract_years(text):
    if not isinstance(text, str) or text.strip() == '':
        return []
    
    # Replace written numbers with digits
    words = text.split()
    for word in words:
        try:
            text = text.replace(word, str(w2n.word_to_num(word)))
        except:
            pass

    # Use regex to find all year-like patterns
    year_patterns = re.findall(r'\b(20\d{2}|2\d|1\d)\b', text)
    year_list = []

    for pattern in year_patterns:
        if len(pattern) == 4:
            year_list.append(str(int(pattern)))  # Convert to string
        elif len(pattern) == 2:
            # Assuming current century for two digit years
            year_list.append(str(2000 + int(pattern)))  # Convert to string

    return year_list  # Returning all occurrences
