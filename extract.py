import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"  # Path to your log file
output_file_path = "extended_logs.csv"  # Output CSV file

# Function to parse a single log entry
def parse_log_entries(log_lines):
    parsed_logs = []
    question, answer, reasoning, source_ref = "", "", "", ""
    timestamp, user, action = None, None, None
    capturing_answer = False

    for line in log_lines:
        line = line.strip()

        # Extract timestamp and user details
        timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*(\w+),\s*([\w\.\-]+@[\w\.\-]+)", line)
        if timestamp_match:
            timestamp, user = timestamp_match.group(1), timestamp_match.group(3)

        # Extract question
        if "qa:" in line:
            question = line.split("qa:", 1)[1].strip()

        # Detect start of answer
        if "result:# Start of answer" in line:
            capturing_answer = True
            answer, reasoning, source_ref = "", "", ""  # Reset previous data
            continue

        # Capture answer content
        if capturing_answer and "end of answer" not in line:
            answer += line + " "

        # Detect end of answer
        if "end of answer" in line:
            capturing_answer = False

        # Extract reasoning
        if "Reasoning:" in line:
            reasoning = line.split("Reasoning:", 1)[1].strip()

        # Extract source reference
        if "SourceRef:" in line:
            source_ref = line.split("SourceRef:", 1)[1].strip()

        # When an answer is fully captured, add the log entry
        if question and answer:
            parsed_logs.append([timestamp, user, question, answer.strip(), reasoning, source_ref])
            question, answer, reasoning, source_ref = "", "", "", ""  # Reset for next entry

    return parsed_logs

# Read the log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# Create DataFrame with new columns
columns = ["Timestamp", "User", "Question", "Answer", "Reasoning", "SourceRef"]
df = pd.DataFrame(parsed_data, columns=columns)

# Add placeholders for metrics
df["Accuracy"] = None
df["Hallucination Score"] = None
df["Relevance"] = None

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"Extended CSV saved as '{output_file_path}'.")
