import pandas as pd
import re
from word2number import w2n
from collections import defaultdict

# Example data including empty rows and non-string values
data = {
    'text': [
        'twenty four, 2024, 24, 2024', 
        '2025, twenty five, 25, 25-26',
        '2024-2025, twenty twenty-five',
        '',
        None,
        'twenty twenty-four',
        '2024'
    ]
}

df = pd.DataFrame(data)

# Function to standardize and extract years
def extract_years(text):
    if not isinstance(text, str) or text.strip() == '':
        return []
    
    # Replace written numbers with digits
    words = text.split()
    normalized_text = text
    for word in words:
        try:
            normalized_text = normalized_text.replace(word, str(w2n.word_to_num(word)))
        except:
            pass

    # Use regex to find all year-like patterns
    year_patterns = re.findall(r'\b(20\d{2}|2\d|1\d)\b', normalized_text)
    year_set = set()

    for pattern in year_patterns:
        if len(pattern) == 4:
            year_set.add(str(int(pattern)))  # Convert to string and add to set
        elif len(pattern) == 2:
            # Assuming current century for two digit years
            year_set.add(str(2000 + int(pattern)))  # Convert to string and add to set

    return list(year_set)  # Returning unique occurrences

# Apply the function and count unique years
df['unique_years'] = df['text'].apply(extract_years)
df['unique_year_counts'] = df['unique_years'].apply(lambda x: {year: x.count(year) for year in x} if x else {})

# Aggregate counts for each year
aggregate_counts = defaultdict(int)
for count_dict in df['unique_year_counts']:
    for year, count in count_dict.items():
        aggregate_counts[year] += count

# Convert the aggregate counts to a DataFrame
year_df = pd.DataFrame(list(aggregate_counts.items()), columns=['Year', 'Frequency'])

# Display the year_df DataFrame
import ace_tools as tools; tools.display_dataframe_to_user(name="Year Frequency", dataframe=year_df)

# Plot the bar graph
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.bar(year_df['Year'], year_df['Frequency'])
plt.xlabel('Year')
plt.ylabel('Frequency')
plt.title('Year Counts')
plt.xticks(rotation=45)
plt.show()
