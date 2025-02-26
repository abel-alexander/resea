import pandas as pd
import re

def extract_qa_lines_with_timestamp(log_file_path):
    qa_data = []

    # Define unwanted names (case insensitive)
    unwanted_names = {"kenny", "anita", "abel", "richa"}

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

    # Email and QA pattern
    qa_pattern = re.compile(r'([\w\.-]+@[\w\.-]+).*?qa:\s*(.+)', re.IGNORECASE)

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            timestamp_match = timestamp_pattern.match(line)
            qa_match = qa_pattern.search(line)

            if timestamp_match and qa_match:
                timestamp = timestamp_match.group(1)
                email = qa_match.group(1)
                question = qa_match.group(2).strip()

                # Skip unwanted names
                if any(name in email.lower() for name in unwanted_names):
                    continue

                qa_data.append([timestamp, email, question])

    df_qa = pd.DataFrame(qa_data, columns=["Timestamp", "Email", "Question"])
    df_qa["Timestamp"] = pd.to_datetime(df_qa["Timestamp"])  # Convert to datetime
    return df_qa

def extract_inference_lines_with_timestamp(log_file_path):
    inference_data = []

    # Define unwanted names
    unwanted_names = {"kenny", "anita", "abel", "richa"}

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

    # Email and inference pattern
    inference_pattern = re.compile(r'([\w\.-]+@[\w\.-]+).*?inference:result:\s*(.+)', re.IGNORECASE)

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            timestamp_match = timestamp_pattern.match(line)
            inference_match = inference_pattern.search(line)

            if timestamp_match and inference_match:
                timestamp = timestamp_match.group(1)
                email = inference_match.group(1)
                answer = inference_match.group(2).strip()

                # Skip unwanted names
                if any(name in email.lower() for name in unwanted_names):
                    continue

                inference_data.append([timestamp, email, answer])

    df_inference = pd.DataFrame(inference_data, columns=["Timestamp", "Email", "Answer"])
    df_inference["Timestamp"] = pd.to_datetime(df_inference["Timestamp"])  # Convert to datetime
    return df_inference

def merge_qa_inference(df_qa, df_inference):
    """
    Merge QA and Inference DataFrames by Email and Closest Timestamp.
    """
    df_qa = df_qa.sort_values(by=["Email", "Timestamp"])
    df_inference = df_inference.sort_values(by=["Email", "Timestamp"])

    df_qa["Answer"] = None  # Initialize Answer column

    # Iterate over QA DataFrame and find closest answer timestamp
    for i, row in df_qa.iterrows():
        email = row["Email"]
        timestamp = row["Timestamp"]

        # Find all answers from the same email
        possible_answers = df_inference[df_inference["Email"] == email]

        # Find the first answer that happens AFTER the question
        closest_answer = possible_answers[possible_answers["Timestamp"] >= timestamp].head(1)

        if not closest_answer.empty:
            df_qa.at[i, "Answer"] = closest_answer["Answer"].values[0]

    return df_qa

# Usage
log_file_path = "path/to/cleaned_logfile.txt"  # Replace with actual path

df_qa = extract_qa_lines_with_timestamp(log_file_path)
df_inference = extract_inference_lines_with_timestamp(log_file_path)

df_final = merge_qa_inference(df_qa, df_inference)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="Final QA Data", dataframe=df_final)
