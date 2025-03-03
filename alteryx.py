import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

def evaluate_summary(input_text, summary):
    """
    Evaluates a generated summary against the original input text.
    Computes standard summarization metrics, along with accuracy, hallucination, and usefulness scores.

    Parameters:
    input_text (str): The original full text.
    summary (str): The generated summary.

    Returns:
    dict: A dictionary with computed metrics, aggregate scores, and interpretation comments.
    """

    # Preprocess text: Lowercase and remove punctuation
    def preprocess(text):
        return text.lower().translate(str.maketrans('', '', string.punctuation))

    input_clean = preprocess(input_text)
    summary_clean = preprocess(summary)

    # Tokenize
    input_tokens = input_clean.split()
    summary_tokens = summary_clean.split()

    # BLEU score with smoothing
    smoothie = SmoothingFunction().method4
    bleu_score = sentence_bleu([input_tokens], summary_tokens, smoothing_function=smoothie)

    # METEOR score
    meteor = meteor_score([input_tokens], summary_tokens)

    # TF-IDF Cosine Similarity (Measures semantic similarity → used for accuracy & hallucination)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([input_clean, summary_clean])
    cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    # Compression Ratio (Measures how much the summary compresses the original text)
    compression_ratio = len(input_tokens) / max(len(summary_tokens), 1)

    # Coverage (How much of the input text is included in the summary)
    coverage = len(set(summary_tokens).intersection(set(input_tokens))) / max(len(input_tokens), 1)

    # Repetition (Ratio of repeated words in the summary → higher means redundant)
    repetition = 1 - (len(set(summary_tokens)) / max(len(summary_tokens), 1))

    # Novelty (How much of the summary is new compared to the input)
    novelty = 1 - coverage

    # Named Entity Overlap (Detects hallucination by checking if the same entities exist in both)
    def named_entity_overlap(input_text, summary):
        def extract_entities(text):
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            chunked = ne_chunk(pos_tags)
            entities = { " ".join(c[0] for c in chunk) for chunk in chunked if hasattr(chunk, 'label') }
            return entities

        input_entities = extract_entities(input_text)
        summary_entities = extract_entities(summary)

        overlap = len(input_entities.intersection(summary_entities)) / max(len(summary_entities), 1)
        return overlap  # Lower = More hallucination risk

    entity_overlap = named_entity_overlap(input_text, summary)

    # Aggregate Scores
    accuracy_score = (cosine_sim + coverage + bleu_score) / 3
    hallucination_score = 1 - ((cosine_sim + coverage + entity_overlap) / 3)  # Lower is better
    usefulness_score = (compression_ratio + (1 - repetition) + (1 - hallucination_score)) / 3

    # Generate Dynamic Interpretation Based on Scores
    def interpret_accuracy(score):
        if score > 0.8:
            return "The summary is highly accurate, capturing key details from the original text."
        elif score > 0.6:
            return "The summary is mostly accurate but may omit some minor details."
        else:
            return "The summary may not accurately capture the original content."

    def interpret_hallucination(score):
        if score < 0.2:
            return "The summary is well-grounded and does not introduce false information."
        elif score < 0.5:
            return "The summary introduces some unverified details but is mostly reliable."
        else:
            return "The summary contains a significant amount of hallucinated (made-up) content."

    def interpret_usefulness(score):
        if score > 0.8:
            return "The summary is concise, relevant, and avoids unnecessary repetition."
        elif score > 0.6:
            return "The summary is useful but could be slightly more concise."
        else:
            return "The summary may contain unnecessary details or lack clarity."

    # Attach Interpretations
    interpretations = {
        "Accuracy Interpretation": interpret_accuracy(accuracy_score),
        "Hallucination Interpretation": interpret_hallucination(hallucination_score),
        "Usefulness Interpretation": interpret_usefulness(usefulness_score),
    }

    return {
        "BLEU": bleu_score,
        "METEOR": meteor,
 
