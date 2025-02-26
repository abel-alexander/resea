import re

def remove_sum_blocks(log_file_path, cleaned_file_path):
    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')
    
    keep_lines = []
    ignore_lines = False  # Flag to ignore lines after 'sum:'

    with open(log_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        # Check if the line starts with a timestamp (New log entry)
        if timestamp_pattern.match(line):
            ignore_lines = False  # Stop ignoring when a new timestamp appears

        # Detect 'sum:' line → Start ignoring
        if "sum:" in line.lower():
            ignore_lines = True  # Start ignoring until next timestamp
            continue  # Skip this line

        # Keep the line if we are not in an ignored block
        if not ignore_lines:
            keep_lines.append(line)

    # Save the cleaned log file
    with open(cleaned_file_path, 'w', encoding='utf-8') as file:
        file.writelines(keep_lines)

    print(f"Cleaned log saved to: {cleaned_file_path}")

# Usage
log_file_path = "path/to/your/logfile.txt"  # Replace with actual file path
cleaned_file_path = "path/to/cleaned_logfile.txt"  # Output file path

