from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from bert_score import score as bert_score
import re
from nltk.stem import PorterStemmer

# Constants for GPU cost
NUM_GPUS = 3  # Number of GPUs used
GPU_COST_PER_HOUR = 3  # Cost per GPU per hour in USD

# Preprocessing function
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    words = text.split()
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]  # Stemming
    return ' '.join(words)

# Function to calculate metrics
def calculate_metrics_with_advanced_scores(df):
    smoothing_function = SmoothingFunction().method1  # For BLEU smoothing
    bleu_scores = []
    meteor_scores = []
    bert_scores_f1 = []
    # rouge1_scores = []  # Commented out
    # rouge2_scores = []  # Commented out
    # rougeL_scores = []  # Commented out
    gpu_costs = []

    # Initialize ROUGE scorer
    # rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)  # Commented out

    for idx, row in df.iterrows():
        # Reference and hypothesis
        reference = row['Reference']
        hypothesis = row['Llama3-v1']

        # Skip if hypothesis or reference is missing
        if pd.isna(reference) or pd.isna(hypothesis):
            bleu_scores.append(None)
            meteor_scores.append(None)
            bert_scores_f1.append(None)
            # rouge1_scores.append(None)  # Commented out
            # rouge2_scores.append(None)  # Commented out
            # rougeL_scores.append(None)  # Commented out
            gpu_costs.append(None)
            continue

        # Preprocess the reference and hypothesis
        preprocessed_reference = preprocess(reference)
        preprocessed_hypothesis = preprocess(hypothesis)

        # BLEU Score
        bleu = sentence_bleu(
            [preprocessed_reference.split()], 
            preprocessed_hypothesis.split(), 
            smoothing_function=smoothing_function
        )
        bleu_scores.append(bleu)

        # METEOR Score
        meteor = meteor_score([preprocessed_reference], preprocessed_hypothesis)
        meteor_scores.append(meteor)

        # BERTScore
        P, R, F1 = bert_score([hypothesis], [reference], lang="en", verbose=False)
        bert_scores_f1.append(F1.mean().item())

        # ROUGE Scores (Commented out for now)
        # rouge_scores = rouge.score(preprocessed_hypothesis, preprocessed_reference)
        # rouge1_scores.append(rouge_scores['rouge1'].fmeasure)
        # rouge2_scores.append(rouge_scores['rouge2'].fmeasure)
        # rougeL_scores.append(rouge_scores['rougeL'].fmeasure)

        # GPU Cost Calculation
        time_taken = row['time taken']  # In seconds
        time_in_hours = time_taken / 3600  # Convert time to hours
        gpu_cost = NUM_GPUS * time_in_hours * GPU_COST_PER_HOUR
        gpu_costs.append(gpu_cost)

    # Add metrics to the DataFrame
    df['BLEU'] = bleu_scores
    df['METEOR'] = meteor_scores
    df['BERTScore_F1'] = bert_scores_f1
    # df['ROUGE-1'] = rouge1_scores  # Commented out
    # df['ROUGE-2'] = rouge2_scores  # Commented out
    # df['ROUGE-L'] = rougeL_scores  # Commented out
    df['GPU Cost (USD)'] = gpu_costs

    return df
