import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "extended_logs.csv"

# Function to extract details from logs
def parse_log_entries(log_lines):
    parsed_logs = []
    timestamp, user_id, name, email = None, None, None, None
    question, answer, reasoning, source_ref = "", "", "", ""
    capturing_answer = False

    for line in log_lines:
        line = line.strip()

        # Extract timestamp, user_id, name, and email
        user_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*(\w+),\s*([\w\s]+),\s*([\w\.-]+@[\w\.-]+)", line)
        if user_match:
            timestamp, user_id, name, email = user_match.groups()

        # Extract question (ensuring it's not a system message)
        if line.startswith("qa:") and "result:#" not in line:
            question = line.split("qa:", 1)[1].strip()

        # Detect start of answer
        if "result:# Start of answer" in line:
            capturing_answer = True
            answer = ""  # Reset previous answer
            continue  # Skip this line

        # Capture answer content
        if capturing_answer and "end of answer" not in line:
            answer += line + " "

        # Detect end of answer
        if "end of answer" in line:
            capturing_answer = False
            answer = answer.strip()

        # Extract reasoning
        if "Reasoning:" in line:
            reasoning = line.split("Reasoning:", 1)[1].strip()

        # Extract source reference
        if "SourceRef:" in line:
            source_ref = line.split("SourceRef:", 1)[1].strip()

        # Save the complete entry when an answer is captured
        if timestamp and user_id and email and question and answer:
            parsed_logs.append([timestamp, user_id, name, email, question, answer, reasoning, source_ref])
            # Reset for the next QA pair
            question, answer, reasoning, source_ref = "", "", "", ""

    return parsed_logs

# Read log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# Create DataFrame with structured columns
columns = ["Timestamp", "User ID", "Name", "Email", "Question", "Answer", "Reasoning", "SourceRef"]
df = pd.DataFrame(parsed_data, columns=columns)

# Add placeholders for evaluation metrics
df["Accuracy"] = None
df["Hallucination Score"] = None
df["Relevance"] = None

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"Extended CSV saved as '{output_file_path}'.")
