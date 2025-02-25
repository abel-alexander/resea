from collections import Counter
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure necessary NLTK resources are downloaded
nltk.download('stopwords')
nltk.download('punkt')

def keyword_frequency(text, special_phrases=None, keywords_to_remove=None, top_n=10):
    # Initialize counter
    unigram_freq_counter = Counter()

    # Ensure default values for optional parameters
    if special_phrases is None:
        special_phrases = []
    if keywords_to_remove is None:
        keywords_to_remove = set()

    # Convert special phrases into underscore-separated versions
    special_phrases_dict = {phrase.lower(): "_".join(phrase.lower().split()) for phrase in special_phrases}

    # Convert text to lowercase
    text = text.lower()

    # Replace special phrases with underscore versions
    for phrase, replacement in special_phrases_dict.items():
        text = text.replace(phrase, replacement)

    # Tokenize text correctly into words
    words = word_tokenize(text)

    # Remove stopwords and unwanted words
    stop_words = set(stopwords.words("english"))
    filtered_words = [w for w in words if w.isalpha() and w not in stop_words and w not in keywords_to_remove]

    # Update frequency counter
    unigram_freq_counter.update(filtered_words)

    # Convert to DataFrame and get the top N keywords
    unigram_df = pd.DataFrame(unigram_freq_counter.items(), columns=['Keyword', 'Frequency']).sort_values(
        by='Frequency', ascending=False
    )

    return unigram_df['Keyword'].head(top_n).tolist()  # Return top N keywords as an array

# Example Usage
text = "This is a sample text for keyword extraction. Keyword analysis is important in machine learning!"
special_phrases = ["keyword extraction", "machine learning"]
keywords_to_remove = {"is", "a", "in"}

top_10_keywords = keyword_frequency(text, special_phrases, keywords_to_remove)
print(top_10_keywords)
