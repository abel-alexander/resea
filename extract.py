import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "extended_logs.csv"

# Function to parse log entries correctly
def parse_log_entries(log_lines):
    parsed_logs = []
    timestamp, user_id, name, email, question = None, None, None, None, None
    answer, reasoning, source_ref = "", "", ""
    capturing_answer = False

    for i, line in enumerate(log_lines):
        line = line.strip()

        # Extract timestamp, user_id, name, email, and question
        user_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*([\w\d]+),\s*([\w\s]+),\s*([\w\.-]+@[\w\.-]+),\s*qa:(.*)", line)
        if user_match:
            timestamp, user_id, name, email, question = user_match.groups()
            continue  # Move to the next line

        # Detect start of answer
        if "qa:result:# Start of answer" in line:
            capturing_answer = True
            answer, reasoning, source_ref = "", "", ""  # Reset previous values
            continue  # Skip this line

        # Capture answer content
        if capturing_answer:
            if line.startswith("Answer:"):
                answer = line.replace("Answer:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
            elif line.startswith("SourceRef:"):
                source_ref = line.replace("SourceRef:", "").strip()

            # Detect end of answer
            if "# end of answer" in line:
                capturing_answer = False
                # Save extracted data only if valid
                if all([timestamp, user_id, name, email, question, answer]):
                    parsed_logs.append([timestamp, user_id, name, email, question, answer, reasoning, source_ref])
                # Reset variables for the next QA pair
                timestamp, user_id, name, email, question = None, None, None, None, None
                answer, reasoning, source_ref = "", "", ""

    return parsed_logs

# Read the log file
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
