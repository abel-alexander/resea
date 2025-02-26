import pandas as pd
import re

def extract_qa_data(log_file_path):
    qa_data = []
    current_email = None
    current_question = None
    current_answer = None
    collecting_answer = False
    
    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Detect the QA question line
            qa_match = re.search(r'([\w\.-]+@[\w\.-]+).*?qa:\s*(.+)', line, re.IGNORECASE)
            if qa_match:
                if current_email and current_question and current_answer:
                    qa_data.append([current_email, current_question, current_answer.strip()])
                
                current_email = qa_match.group(1)
                current_question = qa_match.group(2).strip()
                current_answer = ""
                collecting_answer = False  # Reset answer collection

            # Detect the start of the answer
            if "inference:result" in line:
                collecting_answer = True  # Start collecting answer
                continue

            # Collect answer until we hit `#end of answer`
            if collecting_answer:
                if "#end of answer" in line:
                    collecting_answer = False
                    continue
                current_answer += line.strip() + " "

    # Append last QA pair
    if current_email and current_question and current_answer:
        qa_data.append([current_email, current_question, current_answer.strip()])
    
    # Convert to DataFrame
    df = pd.DataFrame(qa_data, columns=["Email", "Question", "Answer"])
    return df

# Usage
log_file_path = "path/to/your/logfile.txt"  # Replace with the actual file path
df = extract_qa_data(log_file_path)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="QA Data", dataframe=df)
