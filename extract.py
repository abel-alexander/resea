import pandas as pd
from rouge_score import rouge_scorer

def calculate_rouge_scores(text_pairs):
    """
    Takes a list of pairs of texts and returns a DataFrame with each text in separate columns
    and multiple ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L) in additional columns.
    
    Parameters:
    text_pairs (list of tuples): List where each element is a tuple containing two texts.
    
    Returns:
    pd.DataFrame: DataFrame with columns 'Text1', 'Text2', and ROUGE scores (precision, recall, and F1).
    """
    # Initialize a DataFrame with each text in separate columns
    df = pd.DataFrame(text_pairs, columns=['Text1', 'Text2'])

    # Initialize the ROUGE scorer with the metrics we want to calculate
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    # Calculate ROUGE scores for each pair and store them in lists
    rouge1_precision, rouge1_recall, rouge1_f1 = [], [], []
    rouge2_precision, rouge2_recall, rouge2_f1 = [], [], []
    rougeL_precision, rougeL_recall, rougeL_f1 = [], [], []

    for text1, text2 in text_pairs:
        scores = scorer.score(text1, text2)
        
        # ROUGE-1
        rouge1_precision.append(scores['rouge1'].precision)
        rouge1_recall.append(scores['rouge1'].recall)
        rouge1_f1.append(scores['rouge1'].fmeasure)
        
        # ROUGE-2
        rouge2_precision.append(scores['rouge2'].precision)
        rouge2_recall.append(scores['rouge2'].recall)
        rouge2_f1.append(scores['rouge2'].fmeasure)
        
        # ROUGE-L
        rougeL_precision.append(scores['rougeL'].precision)
        rougeL_recall.append(scores['rougeL'].recall)
        rougeL_f1.append(scores['rougeL'].fmeasure)
    
    # Add the ROUGE scores to the DataFrame
    df['ROUGE-1 Precision'] = rouge1_precision
    df['ROUGE-1 Recall'] = rouge1_recall
    df['ROUGE-1 F1'] = rouge1_f1
    df['ROUGE-2 Precision'] = rouge2_precision
    df['ROUGE-2 Recall'] = rouge2_recall
    df['ROUGE-2 F1'] = rouge2_f1
    df['ROUGE-L Precision'] = rougeL_precision
    df['ROUGE-L Recall'] = rougeL_recall
    df['ROUGE-L F1'] = rougeL_f1

    return df

# Example usage:
text_pairs = [
    ("This is a sample text.", "This is another example of text."),
    ("Data science is great.", "Machine learning is a subset of data science."),
    ("Hello world!", "Hello, how are you?")
]

df = calculate_rouge_scores(text_pairs)
print(df)
