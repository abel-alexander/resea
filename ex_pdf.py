from collections import Counter
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

def keyword_frequency(texts, special_phrases, keywords_to_remove):
    # Initialize counter object to hold the frequencies for unigrams
    unigram_freq_counter = Counter()

    # Get the English Stopwords list
    pre_stop_words = set(stopwords.words("english"))
    stop_words = pre_stop_words.union({word for phrase in special_phrases for word in phrase.lower().split()})

    for text in texts:
        # Convert to lowercase
        text = str(text).lower()

        # Normalize special phrases
        for phrase in special_phrases:
            text = text.replace(phrase.lower(), "_".join(phrase.lower().split()))

        # Tokenize text into words
        words = word_tokenize(text)

        # Remove stopwords, non-alphabetic words, and unwanted keywords
        filtered_unigrams = [w for w in words if w.isalpha() and w not in stop_words and w not in keywords_to_remove]

        # Update frequency counter
        unigram_freq_counter.update(filtered_unigrams)

    # Convert to DataFrame and get the top 10 keywords
    unigram_df = pd.DataFrame(unigram_freq_counter.items(), columns=['Keyword', 'Frequency']).sort_values(
        by='Frequency', ascending=False
    )

    # Return top 10 keywords as an array
    return unigram_df['Keyword'].head(10).tolist()
