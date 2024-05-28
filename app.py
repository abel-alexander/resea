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

def extract_years(text):
    if not isinstance(text, str):
        text = str(text)  # Convert non-string to string
    
    if text.strip() == '':
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




import pandas as pd

# Sample DataFrame
data = {
    'Interested in P': ['Yes', 'No', 'I am interested in P, yes', 'no, not interested', 'Absolutely yes!'],
    'Interested in M': ['No', 'Yes', 'Maybe, yes', 'No thanks', 'Sure, yes']
}

df = pd.DataFrame(data)

# Function to check for 'yes' or 'no'
def check_interest(text):
    if isinstance(text, str):
        text_lower = text.lower()
        if 'yes' in text_lower:
            return 'yes'
        elif 'no' in text_lower:
            return 'no'
    return 'undecided'

# Apply the function to each relevant column
df['P_Interest'] = df['Interested in P'].apply(check_interest)
df['M_Interest'] = df['Interested in M'].apply(check_interest)

# Count the occurrences of 'yes' and 'no'
p_interest_counts = df['P_Interest'].value_counts()
m_interest_counts = df['M_Interest'].value_counts()

# Display the counts
print("P Interest Counts:")
print(p_interest_counts)

print("\nM Interest Counts:")
print(m_interest_counts)

# Combine counts into a single DataFrame for better visualization
interest_counts_df = pd.DataFrame({
    'Interested in P': p_interest_counts,
    'Interested in M': m_interest_counts
}).fillna(0).astype(int)  # Fill NaN with 0 and convert to int

# Display the combined counts DataFrame
print("\nCombined Interest Counts DataFrame:")
print(interest_counts_df)
