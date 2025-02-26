import os
import re

def remove_sum_blocks(log_file_path, cleaned_file_path):
    timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')
    keep_lines = []
    ignore_lines = False

    with open(log_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        if timestamp_pattern.match(line):
            ignore_lines = False  # Stop ignoring when a new timestamp appears
        if "sum:" in line.lower():
            ignore_lines = True
            continue
        if not ignore_lines:
            keep_lines.append(line)

    with open(cleaned_file_path, 'w', encoding='utf-8') as file:
        file.writelines(keep_lines)

    if os.path.exists(cleaned_file_path):
        print(f"✅ Cleaned file saved at: {cleaned_file_path}")
    else:
        print("❌ Error: File not created.")

# Usage
log_file_path = "path/to/your/logfile.txt"  # Replace with actual path
cleaned_file_path = "path/to/cleaned_logfile.txt"  # Replace with full path if needed

remove_sum_blocks(log_file_path, cleaned_file_path)
