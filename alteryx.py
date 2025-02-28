import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score

nltk.download('wordnet')

def calculate_summary_metrics(reference, summary):
    """
    Computes evaluation metrics for summarization.

    Parameters:
    reference (str): The ground-truth summary.
    summary (str): The generated summary.

    Returns:
    dict: A dictionary with computed metrics.
    """
    
    # Preprocess text: Lowercase and remove punctuation
    def preprocess(text):
        return text.lower().translate(str.maketrans('', '', string.punctuation))

    reference_clean = preprocess(reference)
    summary_clean = preprocess(summary)

    # Tokenize
    ref_tokens = reference_clean.split()
    summary_tokens = summary_clean.split()

    # BLEU score with smoothing
    smoothie = SmoothingFunction().method4
    bleu_score = sentence_bleu([ref_tokens], summary_tokens, smoothing_function=smoothie)

    # METEOR score
    meteor = meteor_score([ref_tokens], summary_tokens)

    # TF-IDF Cosine Similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([reference_clean, summary_clean])
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    # Compression Ratio
    compression_ratio = len(ref_tokens) / max(len(summary_tokens), 1)

    # Coverage (How much of the original content is included in the summary)
    coverage = len(set(summary_tokens).intersection(set(ref_tokens))) / max(len(ref_tokens), 1)

    # Repetition (Ratio of repeated words in the summary)
    repetition = 1 - (len(set(summary_tokens)) / max(len(summary_tokens), 1))

    # Novelty (How much of the summary is new compared to the reference)
    novelty = 1 - coverage

    return {
        "BLEU": bleu_score,
        "METEOR": meteor,
        "Cosine Similarity": cosine_sim,
        "Compression Ratio": compression_ratio,
        "Coverage": coverage,
        "Repetition": repetition,
        "Novelty": novelty
    }

# Example Usage
reference_text = "The cat sat on the mat and looked at the moon."
summary_text = "The cat sat on the mat."

metrics = calculate_summary_metrics(reference_text, summary_text)
print(metrics)
