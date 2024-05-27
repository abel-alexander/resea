import pandas as pd
import re
from word2number import w2n

# Example data including empty rows
data = {
    'text': [
        'twenty four, 2024, 24, 2024', 
        '2025, twenty five, 25, 25-26',
        '2024-2025, twenty twenty-five',
        '',
        None,
        'twenty twenty-four'
    ]
}

df = pd.DataFrame(data)

# Function to standardize and extract years
def extract_years(text):
    if not text or text.strip() == '':
        return []
    
    # Replace written numbers with digits
    for word in text.split():
        try:
            text = text.replace(word, str(w2n.word_to_num(word)))
        except:
            pass

    # Use regex to find all year-like patterns
    year_patterns = re.findall(r'\b(20\d{2}|2\d|1\d)\b', text)
    year_list = []

    for pattern in year_patterns:
        if len(pattern) == 4:
            year_list.append(int(pattern))
        elif len(pattern) == 2:
            # Assuming current century for two digit years
            year_list.append(2000 + int(pattern))

    return list(set(year_list))

# Apply the function and count unique years
df['unique_years'] = df['text'].apply(extract_years)
df['unique_year_counts'] = df['unique_years'].apply(lambda x: {year: x.count(year) for year in set(x)} if x else {})

# Display the dataframe
import ace_tools as tools; tools.display_dataframe_to_user(name="Year Counts", dataframe=df)

df[['text', 'unique_years', 'unique_year_counts']]
