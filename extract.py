import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "qa_cleaned.csv"

# Users to exclude
excluded_users = {"Abel", "Anita", "Kenny"}

# Function to extract questions and answers correctly
def parse_log_entries(log_lines):
    parsed_logs = []
    question, user, timestamp = None, None, None
    answer_parts = []
    capturing_answer = False
    total_questions = 0
    total_answers = 0

    for line in log_lines:
        line = line.strip()

        # Extract timestamp, user, and question
        match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*[\w\d]+,\s*([\w\s]+),\s*([\w\.-]+@[\w\.-]+),\s*qa:(?!result:)(.*)", line)
        if match:
            timestamp, user, email, question = match.groups()

            # Exclude questions from specific users
            if any(excluded in user for excluded in excluded_users):
                continue  

            total_questions += 1
            continue  # Move to next line

        # Detect start of answer (contains "qa:result")
        elif "qa:result" in line:
            capturing_answer = True
            answer_parts = []  # Reset previous answer
            continue  # Skip this line

        # Capture answer content (everything until "# end of answer")
        if capturing_answer:
            if "# end of answer" in line:
                capturing_answer = False
                full_answer = " ".join(answer_parts).strip()  # Combine answer text
                total_answers += 1  

                # ✅ Store unique Q&A pair
                if question and full_answer:
                    parsed_logs.append([timestamp, user, question, full_answer])
                    question = None  # Reset for next question

                answer_parts = []
            else:
                answer_parts.append(line)  # Collect answer lines

    print(f"✅ Extracted {total_questions} questions and {total_answers} answers.")
    return parsed_logs

# Read the log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# Create DataFrame
df = pd.DataFrame(parsed_data, columns=["Timestamp", "User", "Question", "Answer"])

# Remove exact duplicate rows
df.drop_duplicates(inplace=True)

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"✅ Cleaned QA pairs saved in '{output_file_path}'.")

# Verify final count
print(f"✅ Final row count after deduplication: {len(df)}")
