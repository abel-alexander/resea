import pandas as pd
import re

def extract_qa_data(log_file_path):
    qa_data = []
    current_email = None
    current_question = None
    current_answer = None
    collecting_answer = False

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

    with open(log_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        # Detect if the line starts with a timestamp
        timestamp_match = timestamp_pattern.match(line)
        
        # Detect QA question line
        qa_match = re.search(r'([\w\.-]+@[\w\.-]+).*?qa:\s*(.+)', line, re.IGNORECASE)
        if qa_match and timestamp_match:
            # Store previous QA pair if one exists
            if current_email and current_question and current_answer:
                qa_data.append([current_email, current_question, current_answer.strip()])
            
            # Start new question
            current_email = qa_match.group(1)
            current_question = qa_match.group(2).strip()
            current_answer = ""
            collecting_answer = False  # Reset answer collection

        # Find first `inference:result` **after** a question (this line must have a timestamp)
        if "inference:result" in line and timestamp_match and current_question and not collecting_answer:
            collecting_answer = True  # Start collecting answer
            continue  # Move to next line to start answer collection

        # Collect answer lines until another timestamp appears
        if collecting_answer:
            if timestamp_match:  # Stop collecting when a new timestamp is detected
                collecting_answer = False
                continue
            current_answer += line.strip() + " "

    # Append the last QA pair if valid
    if current_email and current_question and current_answer:
        qa_data.append([current_email, current_question, current_answer.strip()])

    # Convert to DataFrame
    df = pd.DataFrame(qa_data, columns=["Email", "Question", "Answer"])
    return df

# Usage
log_file_path = "path/to/your/logfile.txt"  # Replace with actual file path
df = extract_qa_data(log_file_path)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="QA Data", dataframe=df)
