# Input file
input_file_path = "usagelog.txt"

# Initialize counters
qa_count = 0
qa_result_count = 0
summary_count = 0

# Read the log file line by line
with open(input_file_path, "r", encoding="utf-8") as file:
    log_lines = file.readlines()

# Count occurrences
for line in log_lines:
    line = line.strip()

    if "qa:" in line and "qa:result" not in line:
        qa_count += 1  # Count questions
    
    if "qa:result" in line:
        qa_result_count += 1  # Count answers

    if "summary" in line.lower():  
        summary_count += 1  # Count summary entries

# Print results
print(f"✅ Total 'qa:' (Questions): {qa_count}")
print(f"✅ Total 'qa:result' (Answers): {qa_result_count}")
print(f"✅ Total 'summary' occurrences: {summary_count}")
