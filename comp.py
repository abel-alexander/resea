input_file_path = "usagelog.txt"
output_file_path = "filtered_usage.txt"

with open(input_file_path, "r", encoding="utf-8", errors="ignore") as infile:
    lines = infile.readlines()

keep_lines = []
capture = False

for line in lines:
    line = line.strip()  # Remove unnecessary whitespace

    # Capture any line with 'qa:' (ensures questions are included)
    if "qa:" in line:
        keep_lines.append(line)

    # If 'qa:result' appears, start capturing
    if "qa:result" in line:
        capture = True
        keep_lines.append(line)

    # If capturing, add all lines
    elif capture:
        keep_lines.append(line)

    # If '# end of answer' appears, ensure only one occurrence
    if "# end of answer" in line:
        if capture:  # Ensure we were capturing
            keep_lines.append(line)
            capture = False  # Stop capturing after writing it

# Remove duplicate consecutive `# end of answer` entries
filtered_output = []
prev_line = ""
for line in keep_lines:
    if line == "# end of answer" and prev_line == "# end of answer":
        continue  # Skip duplicate occurrences
    filtered_output.append(line)
    prev_line = line  # Track last written line

# Write to the output file
with open(output_file_path, "w", encoding="utf-8") as outfile:
    outfile.write("\n".join(filtered_output))

print(f"Filtered lines saved to {output_file_path}")
