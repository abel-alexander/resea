import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "simplified_logs.csv"

# Function to parse log entries
def parse_log_entries(log_lines):
    parsed_logs = []
    timestamp, user, question = None, None, None
    answer_parts = []
    capturing_answer = False

    for line in log_lines:
        line = line.strip()

        # Extract timestamp, user, and question
        question_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*[\w\d]+,\s*([\w\s]+),\s*([\w\.-]+@[\w\.-]+),\s*qa:(?!result:)(.*)", line)
        if question_match:
            timestamp, user, question = question_match.group(1), question_match.group(2), question_match.group(4)
            continue  # Move to the next line

        # Detect start of answer
        if "qa:result:# Start of answer" in line:
            capturing_answer = True
            answer_parts = []  # Reset previous answer
            continue

        # Capture answer content
        if capturing_answer:
            if "# end of answer" in line:
                capturing_answer = False
                # Save entry only if valid
                if timestamp and user and question and answer_parts:
                    parsed_logs.append([timestamp, user, question, " ".join(answer_parts).strip()])
                timestamp, user, question = None, None, None  # Reset for next QA pair
                answer_parts = []
            else:
                answer_parts.append(line)  # Collect all answer parts (Answer, Reasoning, SourceRef)

    return parsed_logs

# Read the log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# Create DataFrame with structured columns
columns = ["Timestamp", "User", "Question", "Answer"]
df = pd.DataFrame(parsed_data, columns=columns)

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"✅ Simplified CSV saved as '{output_file_path}'.")
