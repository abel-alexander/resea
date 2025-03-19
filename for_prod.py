import re
import pandas as pd

input_file_path = "usagelog.txt"

# List of PIB names to check against
pib_list = ["Starbucks", "Snap", "Tesla", "Walmart"]  # Expand as needed

# Regex to correctly capture timestamp, username, and length
timestamp_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+,\s*[^,]+,\s*([^,]+),.*?sum:@:len-(\d+):?(.*)?")

# Read file into memory
with open(input_file_path, "r", encoding="utf-8", errors="ignore") as infile:
    lines = infile.readlines()

# Data storage
data = []
capture = False
current_summary = []
timestamp = ""
user_name = ""
summary_length = 0
section_name = ""
pib_name = ""  # Default PIB name is empty

for line in lines:
    line = line.strip()  # Remove unnecessary spaces

    # Check if line starts with timestamp and contains "sum:@"
    match = timestamp_pattern.match(line)
    if match:
        # If capturing a previous summary, save it
        if capture and current_summary:
            # Remove the first line before saving summary
            cleaned_summary = "\n".join(current_summary[1:]).strip()
            data.append([timestamp, user_name, summary_length, section_name, pib_name, cleaned_summary])

        # Extract new summary metadata
        timestamp, user_name, summary_length, section_name = match.groups()
        summary_length = int(summary_length)  # Convert length to integer
        section_name = section_name.strip() if section_name else ""  # Ensure clean section name
        pib_name = ""  # Reset PIB name
        current_summary = [line]  # Store first line (to be removed later)
        capture = True  # Start capturing

    # If another timestamp appears and we were capturing, store the previous summary
    elif re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line):
        if capture and current_summary:
            # Remove the first line before saving summary
            cleaned_summary = "\n".join(current_summary[1:]).strip()
            data.append([timestamp, user_name, summary_length, section_name, pib_name, cleaned_summary])
        capture = False  # Stop capturing
        current_summary = []  # Reset buffer

    # Continue capturing if inside a summary block
    elif capture:
        current_summary.append(line)

        # Check if this line contains any PIB name from the list
        for pib in pib_list:
            if pib in line:
                pib_name = pib  # Assign matching PIB name

# Save the last summary if still in capture mode
if capture and current_summary:
    cleaned_summary = "\n".join(current_summary[1:]).strip()
    data.append([timestamp, user_name, summary_length, section_name, pib_name, cleaned_summary])

# Convert to Pandas DataFrame
df = pd.DataFrame(data, columns=["Timestamp", "User Name", "Length", "Section Name", "PIB Name", "Summary Text"])

# **Remove duplicate summaries (keep first occurrence)**
df = df.drop_duplicates(subset=["Summary Text"], keep="first").reset_index(drop=True)

# Display DataFrame for verification
import ace_tools as tools
tools.display_dataframe_to_user(name="Extracted Summaries", dataframe=df)
