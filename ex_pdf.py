import pandas as pd
import re

def extract_qa_data(cleaned_log_file):
    qa_data = []
    current_email = None
    current_question = None
    current_answer = None
    collecting_answer = False

    # Define unwanted names (case insensitive)
    unwanted_names = {"kenny", "anita", "abel", "richa"}

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')

    with open(cleaned_log_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        timestamp_match = timestamp_pattern.match(line)

        # Detect QA question line
        qa_match = re.search(r'([\w\.-]+@[\w\.-]+).*?qa:\s*(.+)', line, re.IGNORECASE)
        if qa_match and timestamp_match:
            email = qa_match.group(1)
            question = qa_match.group(2).strip()

            # Skip if the email contains an unwanted name
            if any(name in email.lower() for name in unwanted_names):
                continue

            # Store previous QA pair if exists
            if current_email and current_question and current_answer:
                qa_data.append([current_email, current_question, current_answer.strip()])

            # Start new question
            current_email = email
            current_question = question
            current_answer = ""
            collecting_answer = False  # Reset answer collection

        # Detect first `inference:result:` after a question (this line must have a timestamp)
        if "inference:result:" in line and timestamp_match and current_question and not collecting_answer:
            collecting_answer = True  # Start collecting answer
            continue  # Move to next line for answer collection

        # Collect answer lines until another timestamp appears
        if collecting_answer:
            if timestamp_match:  # Stop collecting when a new timestamp is detected
                collecting_answer = False
                continue
            current_answer += line + " "

    # Append the last QA pair if valid
    if current_email and current_question and current_answer:
        qa_data.append([current_email, current_question, current_answer.strip()])

    # Convert to DataFrame
    df = pd.DataFrame(qa_data, columns=["Email", "Question", "Answer"])
    return df

# Usage
cleaned_log_file = "path/to/cleaned_logfile.txt"  # Replace with actual path
df = extract_qa_data(cleaned_log_file)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="QA Data", dataframe=df)
