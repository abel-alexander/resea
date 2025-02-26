import pandas as pd
import re

# Input and output file paths
input_file_path = "usagelog.txt"
output_file_path = "qa_extracted.csv"

# Function to extract email, questions, and answers
def parse_log_entries(log_lines):
    parsed_logs = []
    email, question = None, None
    answer_parts = []
    capturing_answer = False
    total_questions = 0
    total_answers = 0

    for line in log_lines:
        line = line.strip()

        # ✅ Extract Email and Question (qa: but NOT qa:result)
        match = re.match(r".*([\w\.-]+@[\w\.-]+),\s*qa:(?!result:)(.*)", line)
        if match:
            email, question = match.groups()
            total_questions += 1
            continue  

        # ✅ Detect start of answer (qa:result)
        elif "qa:result" in line:
            capturing_answer = True
            answer_parts = []  # Reset previous answer
            continue  

        # ✅ Capture answer content (until "# end of answer")
        if capturing_answer:
            if "# end of answer" in line:
                capturing_answer = False
                full_answer = " ".join(answer_parts).strip()  # Combine answer text
                total_answers += 1  

                # ✅ Store Email, Question, and Answer
                if email and question:
                    parsed_logs.append([email, question, full_answer])
                    email, question = None, None  # Reset for next entry

                answer_parts = []
            else:
                answer_parts.append(line)  

    print(f"✅ Extracted {total_questions} questions and {total_answers} answers.")
    return parsed_logs

# Read the log file
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Process log entries
parsed_data = parse_log_entries(log_lines)

# ✅ Create DataFrame
df = pd.DataFrame(parsed_data, columns=["Email", "Question", "Answer"])

# ✅ Remove exact duplicate rows
df.drop_duplicates(inplace=True)

# ✅ Save to CSV
df.to_csv(output_file_path, index=False)
print(f"✅ Cleaned QA pairs saved in '{output_file_path}'.")

# ✅ Final count verification
print(f"✅ Final row count after deduplication: {len(df)}")
