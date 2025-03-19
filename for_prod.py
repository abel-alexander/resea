import re
import csv

input_file_path = "usagelog.txt"
output_file_path = "filtered_summary.csv"

# List of PIB names to check against
pib_list = ["PIB Document 1", "PIB Report Q3", "Annual PIB Summary"]  # Add more as needed

# Regex pattern to detect the start of a summary block (timestamp, username, sum:@:len)
datestamp_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?,\s*([^,]+),\s*sum:@:len=(\d+)")

# Read the file
with open(input_file_path, "r", encoding="utf-8", errors="ignore") as infile:
    lines = infile.readlines()

summaries = []
capture = False
current_summary = []
timestamp = ""
user_name = ""
summary_length = 0
pib_name = ""  # Default PIB name is empty

for line in lines:
    line = line.strip()  # Clean unnecessary spaces

    # Detect the start of a summary block (datestamp + sum:@:len)
    match = datestamp_pattern.search(line)
    if match:
        # If capturing a previous summary, store it before starting a new one
        if capture and current_summary:
            summaries.append([timestamp, user_name, summary_length, pib_name, "\n".join(current_summary)])

        # Extract new summary details
        timestamp, user_name, summary_length = match.groups()
        summary_length = int(summary_length)  # Convert length to integer
        pib_name = ""  # Reset PIB name for new summary
        current_summary = [line]  # Store first line
        capture = True  # Start capturing

    # If another datestamp appears and we are capturing, store the previous summary and reset
    elif datestamp_pattern.search(line):
        if capture and current_summary:
            summaries.append([timestamp, user_name, summary_length, pib_name, "\n".join(current_summary)])
        capture = False  # Stop capturing
        current_summary = []  # Reset buffer

    # Continue capturing if inside a summary block
    elif capture:
        current_summary.append(line)

        # Check if this line contains any PIB name from the list (but don't use it as a condition for extraction)
        for pib in pib_list:
            if pib in line:
                pib_name = pib  # Assign matching PIB name

# Save the last summary if still in capture mode
if capture and current_summary:
    summaries.append([timestamp, user_name, summary_length, pib_name, "\n".join(current_summary)])

# Write output to a CSV file
with open(output_file_path, "w", encoding="utf-8", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["Timestamp", "User Name", "Length", "PIB Name", "Summary Text"])
    writer.writerows(summaries)

print(f"Extracted summaries saved to {output_file_path}")
