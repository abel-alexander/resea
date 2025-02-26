import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "simplified_logs.csv"

# Function to extract questions and answers
def parse_log_entries(log_lines):
    parsed_logs = []
    question = None
    answer_parts = []
    capturing_answer = False

    for line in log_lines:
        line = line.strip()

        # Detect question (line contains "qa:" but NOT "qa:result")
        if "qa:" in line and "qa:result" not in line:
            question = re.sub(r".*qa:\s*", "", line).strip()  # Extract the question text

        # Detect start of answer (line contains "qa:result")
        elif "qa:result" in line:
            capturing_answer = True
            answer_parts = []  # Reset previous answer
            continue

        # Capture answer content
        if capturing_answer:
            if "# end of answer" in line:
                capturing_answer = False
                full_answer = " ".join(answer_parts).strip()  # Combine answer text
                if question and full_answer:
                    parsed_logs.append([question, full_answer])
                question = None  # Reset for next question
                answer_parts = []
            else:
                answer_parts.append(line)  # Collect answer lines

    return parsed_logs

# Read the log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# Create DataFrame
df = pd.DataFrame(parsed_data, columns=["Question", "Answer"])

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"✅ Simplified CSV saved as '{output_file_path}'.")
