import pandas as pd
import re

# Get the data from Alteryx input (connected dataset)
df = Alteryx.read("#1")  # "#1" refers to the first input to the Python tool

# Example log structure:
# "2024-11-20 08:56:55, Kenny Ku, kenny.ku@bofa.com, qa:result Start QA"
# "2024-11-20 08:57:21, Kenny Ku, kenny.ku@bofa.com, sum:e1n-8308"

# Define a function to extract User ID, Action Type, and Timestamp
def parse_log(log_line):
    # Extract timestamp
    timestamp = re.search(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", log_line)
    timestamp = timestamp.group(0) if timestamp else None

    # Extract action type (qa or sum)
    action_match = re.search(r"(qa|sum):", log_line, re.IGNORECASE)
    action = action_match.group(1).lower() if action_match else None

    # Extract user (assumes email or name is after timestamp)
    user_match = re.search(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}, (.+?),", log_line)
    user = user_match.group(1).strip() if user_match else None

    return timestamp, user, action

# Apply the parsing function to each row
parsed_data = df['log_column'].apply(parse_log)  # Replace 'log_column' with the name of the log text column
parsed_df = pd.DataFrame(parsed_data.tolist(), columns=['Timestamp', 'User', 'Action'])

# Add parsed data back into the original DataFrame (if needed)
output_df = pd.concat([df, parsed_df], axis=1)

# Write the output back to Alteryx
Alteryx.write(output_df, 1)  # "1" refers to the first output anchor
