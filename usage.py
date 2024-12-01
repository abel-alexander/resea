import re
import pandas as pd

# File paths
input_file_path = "input_logs.txt"  # Path to the .txt log file
output_file_path = "parsed_logs.csv"  # Path for the output .csv file

# Function to parse a single log line
def parse_log_line(log_line):
    # Extract timestamp
    timestamp = re.search(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", log_line)
    timestamp = timestamp.group(0) if timestamp else None

    # Extract user (email or name)
    user_match = re.search(r",\s*([\w\.-]+@[\w\.-]+|\w+\s+\w+),", log_line)  # Matches email or "First Last"
    user = user_match.group(1).strip() if user_match else "Unknown"

    # Extract action type (e.g., 'qa' or 'sum')
    action_match = re.search(r"(qa|sum):", log_line, re.IGNORECASE)
    action = action_match.group(1).lower() if action_match else None

    return [timestamp, user, action]

# Read the .txt file line by line
parsed_logs = []
with open(input_file_path, "r", encoding="utf-8") as file:  # Specify encoding here
    for line in file:
        parsed_data = parse_log_line(line.strip())  # Parse each line
        if parsed_data[0]:  # Only include lines with a valid timestamp
            parsed_logs.append(parsed_data)

# Create a DataFrame from the parsed logs
columns = ["Timestamp", "User", "Action"]
df = pd.DataFrame(parsed_logs, columns=columns)

# Save the DataFrame to a .csv file
df.to_csv(output_file_path, index=False)

print(f"Parsed logs saved to {output_file_path}")
