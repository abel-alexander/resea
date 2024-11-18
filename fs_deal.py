from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score

# GPU cost constants
NUM_GPUS = 3  # Number of GPUs used
GPU_COST_PER_HOUR = 3  # Cost per GPU per hour in USD

# Function to calculate metrics
def calculate_metrics_with_gpu_cost(df):
    smoothing_function = SmoothingFunction().method1  # For BLEU smoothing
    bleu_scores = []
    meteor_scores = []
    gpu_costs = []

    for idx, row in df.iterrows():
        # Reference and hypothesis
        reference = row['Reference']
        hypothesis = row['Llama3-v1']

        # Skip if hypothesis or reference is missing
        if pd.isna(reference) or pd.isna(hypothesis):
            bleu_scores.append(None)
            meteor_scores.append(None)
            gpu_costs.append(None)
            continue

        # Sentence BLEU Score
        bleu = sentence_bleu(
            [reference.split()], 
            hypothesis.split(), 
            smoothing_function=smoothing_function
        )
        bleu_scores.append(bleu)

        # METEOR Score
        meteor = meteor_score([reference], hypothesis)
        meteor_scores.append(meteor)

        # GPU Cost Calculation
        time_taken = row['time taken']  # In seconds
        time_in_hours = time_taken / 3600  # Convert time to hours
        gpu_cost = NUM_GPUS * time_in_hours * GPU_COST_PER_HOUR
        gpu_costs.append(gpu_cost)

    # Add metrics to the DataFrame
    df['BLEU'] = bleu_scores
    df['METEOR'] = meteor_scores
    df['GPU Cost'] = gpu_costs

    return df

# Example usage
# Assuming `df` is your DataFrame with the specified columns
df = calculate_metrics_with_gpu_cost(df)
