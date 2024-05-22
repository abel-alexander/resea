import pandas as pd
from rouge_score import rouge_scorer, scoring

# Load the Excel file
file_path = '/mnt/data/your_excel_file.xlsx'
df = pd.read_excel(file_path)

# Initialize the ROUGE scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougel'], use_stemmer=True)
aggregator = scoring.BootstrapAggregator()

# Function to compute ROUGE scores
def compute_rouge_scores(gen_text, ref_text):
    scores = scorer.score(gen_text, ref_text)
    return {
        'rouge1_recall': scores['rouge1'].recall,
        'rouge1_precision': scores['rouge1'].precision,
        'rouge1_fmeasure': scores['rouge1'].fmeasure,
        'rouge2_recall': scores['rouge2'].recall,
        'rouge2_precision': scores['rouge2'].precision,
        'rouge2_fmeasure': scores['rouge2'].fmeasure,
        'rougel_recall': scores['rougel'].recall,
        'rougel_precision': scores['rougel'].precision,
        'rougel_fmeasure': scores['rougel'].fmeasure
    }

# Apply the function to each row
df_scores = df.apply(lambda row: compute_rouge_scores(row['generated_text'], row['reference_text']), axis=1)

# Convert the resulting Series of dictionaries to a DataFrame
df_scores = pd.DataFrame(df_scores.tolist())

# Concatenate the original DataFrame with the ROUGE scores DataFrame
df_result = pd.concat([df, df_scores], axis=1)

# Save the updated DataFrame back to an Excel file
output_file_path = '/mnt/data/your_output_file.xlsx'
df_result.to_excel(output_file_path, index=False)

print(f"ROUGE scores have been computed and saved to {output_file_path}")
