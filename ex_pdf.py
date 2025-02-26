import pandas as pd
import re

def extract_qa_lines(log_file_path):
    qa_data = []

    # Email and QA pattern
    qa_pattern = re.compile(r'([\w\.-]+@[\w\.-]+).*?qa:\s*(.+)', re.IGNORECASE)

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Detect QA question line
            qa_match = qa_pattern.search(line)
            if qa_match:
                email = qa_match.group(1)
                question = qa_match.group(2).strip()
                qa_data.append([email, question])

    # Convert to DataFrame
    df = pd.DataFrame(qa_data, columns=["Email", "Question"])
    return df

# Usage
log_file_path = "path/to/cleaned_logfile.txt"  # Replace with actual file path
df = extract_qa_lines(log_file_path)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="QA Questions", dataframe=df)
