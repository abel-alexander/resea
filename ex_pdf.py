import pandas as pd
import re

def extract_qa_lines_with_timestamp(log_file_path):
    qa_data = []

    # Define unwanted names (case insensitive)
    unwanted_names = {"kenny", "anita", "abel", "richa"}

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

    # Email and QA pattern
    qa_pattern = re.compile(r'([\w\.-]+@[\w\.-]+).*?qa:\s*(.+)', re.IGNORECASE)

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Detect timestamp
            timestamp_match = timestamp_pattern.match(line)

            # Detect QA question line
            qa_match = qa_pattern.search(line)
            if timestamp_match and qa_match:
                timestamp = timestamp_match.group(1)
                email = qa_match.group(1)
                question = qa_match.group(2).strip()

                # Skip if the email contains an unwanted name
                if any(name in email.lower() for name in unwanted_names):
                    continue

                qa_data.append([timestamp, email, question])

    # Convert to DataFrame
    df_qa = pd.DataFrame(qa_data, columns=["Timestamp", "Email", "Question"])
    return df_qa

# Usage
log_file_path = "path/to/cleaned_logfile.txt"  # Replace with actual file path
df_qa = extract_qa_lines_with_timestamp(log_file_path)

# Display extracted data
import ace_tools as tools
tools.display_dataframe_to_user(name="Filtered QA Questions", dataframe=df_qa)
