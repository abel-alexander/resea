import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"  # Your log file
output_file_path = "extended_logs.csv"  # Output CSV

# Function to parse a single log line
def parse_log_line(log_line):
    # Extract timestamp
    timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", log_line)
    timestamp = timestamp_match.group(0) if timestamp_match else None

    # Extract user email or name
    user_match = re.search(r"([\w\.-]+@[\w\.-]+\.\w+)", log_line)  # Matches emails
    user = user_match.group(0).strip() if user_match else "Unknown"

    # Extract action type
    action_match = re.search(r"(qa|result|sum|summary)", log_line, re.IGNORECASE)
    action = action_match.group(0).lower() if action_match else None

    # Extract question
    question_match = re.search(r"question:\s*(.*?)(?=\s*answer:)", log_line, re.IGNORECASE)
    question = question_match.group(1).strip() if question_match else ""

    # Extract answer
    answer_match = re.search(r"answer:\s*(.*)", log_line, re.IGNORECASE)
    answer = answer_match.group(1).strip() if answer_match else ""

    return [timestamp, user, action, question, answer]

# Read log file and process lines
parsed_logs = []
with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        parsed_data = parse_log_line(line.strip())
        if parsed_data[0]:  # Only include valid entries with a timestamp
            parsed_logs.append(parsed_data)

# Create DataFrame with new columns
columns = ["Timestamp", "User", "Action", "Question", "Answer"]
df = pd.DataFrame(parsed_logs, columns=columns)

# Add placeholders for metrics
df["Accuracy"] = None
df["Hallucination Score"] = None
df["Relevance"] = None

# Save the extended CSV
df.to_csv(output_file_path, index=False)
print(f"Extended CSV saved as '{output_file_path}'.")
