import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "qa_extracted.csv"

# Function to extract user queries and answers correctly
def parse_log_entries(log_lines):
    parsed_logs = []
    question = None
    answer_parts = []
    capturing_answer = False
    total_questions = 0
    total_answers = 0

    for line in log_lines:
        line = line.strip()

        # Ignore logs that contain "sum:@"
        if "sum:@" in line:
            continue  # Skip these lines

        # Detect question (contains "qa:" but NOT "qa:result")
        if "qa:" in line and "qa:result" not in line:
            # Extract the question text
            question = re.sub(r".*qa:\s*", "", line).strip()
            total_questions += 1  # Count extracted questions
            continue  # Move to the next line

        # Detect start of answer (contains "qa:result")
        elif "qa:result" in line:
            capturing_answer = True
            answer_parts = []  # Reset previous answer
            continue  # Skip this line

        # Capture answer content (until "# end of answer")
        if capturing_answer:
            if "# end of answer" in line:
                capturing_answer = False
                full_answer = " ".join(answer_parts).strip()  # Combine answer text
                total_answers += 1  # Count extracted answers

                # ✅ Store Q&A pair
                if question:
                    parsed_logs.append([question, full_answer])
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
df = pd.DataFrame(parsed_data, columns=["Question", "Answer"])

# Save to CSV
df.to_csv(output_file_path, index=False)
print(f"✅ Extracted QA pairs saved in '{output_file_path}'.")

# Verify final count
print(f"✅ Final row count: {len(df)} (Should match total extracted questions)")
