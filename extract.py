import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "extended_logs.csv"

# Function to parse log entries
def parse_log_entries(log_lines):
    parsed_logs = []
    current_entry = {
        "Timestamp": None,
        "User ID": None,
        "Name": None,
        "Email": None,
        "Question": None,
        "Answer": None,
        "Reasoning": None,
        "SourceRef": None
    }
    capturing_answer = False

    for line in log_lines:
        line = line.strip()

        # Extract question entry (Timestamp, User ID, Name, Email, Question)
        question_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*([\w\d]+),\s*([\w\s]+),\s*([\w\.-]+@[\w\.-]+),\s*qa:(.*)", line)
        if question_match:
            current_entry["Timestamp"], current_entry["User ID"], current_entry["Name"], current_entry["Email"], current_entry["Question"] = question_match.groups()
            continue  # Move to next line

        # Detect start of answer (ignore this line)
        if "qa:result:# Start of answer" in line:
            capturing_answer = True
            current_entry["Answer"], current_entry["Reasoning"], current_entry["SourceRef"] = "", "", ""  # Reset fields
            continue  # Skip this line

        # Capture answer content
        if capturing_answer:
            if line.startswith("Answer:"):
                current_entry["Answer"] = line.replace("Answer:", "").strip()
            elif line.startswith("Reasoning:"):
                current_entry["Reasoning"] = line.replace("Reasoning:", "").strip()
            elif line.startswith("SourceRef:"):
                current_entry["SourceRef"] = line.replace("SourceRef:", "").strip()

            # Detect end of answer, save entry, and reset variables
            if "# end of answer" in line:
                capturing_answer = False
                parsed_logs.append(current_entry.copy())  # Store the current entry
                current_entry = {
                    "Timestamp": None,
                    "User ID": None,
                    "Name": None,
                    "Email": None,
                    "Question": None,
                    "Answer": None,
                    "Reasoning": None,
                    "SourceRef": None
                }  # Reset for next entry

    return parsed_logs

# Read the log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# Create DataFrame
columns = ["Timestamp", "User ID", "Name", "Email", "Question", "Answer", "Reasoning", "SourceRef"]
df = pd.DataFrame(parsed_data, columns=columns)

# Add placeholders for evaluation metrics
df["Accuracy"] = None
df["Hallucination Score"] = None
df["Relevance"] = None

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"Extended CSV saved as '{output_file_path}'.")
