import pandas as pd
import re

def extract_inference_data(log_file_path):
    inference_data = []
    collecting_answer = False
    current_email = None
    current_timestamp = None
    current_text = []

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

    # Email and inference pattern
    inference_pattern = re.compile(r'([\w\.-]+@[\w\.-]+).*?inference:\s*(.+)', re.IGNORECASE)

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            timestamp_match = timestamp_pattern.match(line)

            # If a new timestamp appears, store the previous inference block
            if timestamp_match and collecting_answer:
                inference_data.append([current_timestamp, current_email, " ".join(current_text).strip()])
                collecting_answer = False
                current_text = []

            # Detect inference line
            inference_match = inference_pattern.search(line)
            if timestamp_match and inference_match:
                current_timestamp = timestamp_match.group(1)
                current_email = inference_match.group(1)
                text_start = inference_match.group(2).strip()

                current_text = [text_start]
                collecting_answer = True
                continue

            # Collect multi-line text until a new timestamp appears
            if collecting_answer:
                current_text.append(line)

    # Append last inference entry if still collecting
    if collecting_answer and current_text:
        inference_data.append([current_timestamp, current_email, " ".join(current_text).strip()])

    # Convert to DataFrame
    df_inference = pd.DataFrame(inference_data, columns=["Timestamp", "Email", "Text"])
    df_inference["Timestamp"] = pd.to_datetime(df_inference["Timestamp"])  # Convert to datetime
    return df_inference

# Usage
log_file_path = "path/to/cleaned_logfile.txt"  # Replace with actual path
df_inference = extract_inference_data(log_file_path)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="Extracted Inference Data", dataframe=df_inference)
