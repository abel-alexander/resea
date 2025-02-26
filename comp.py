input_file_path = "usagelog.txt"
output_file_path = "filtered_usage.txt"

# Open file and ensure correct encoding
with open(input_file_path, "r", encoding="utf-8", errors="ignore") as infile:
    lines = infile.readlines()

keep_lines = []
capture = False

for line in lines:
    line = line.strip()  # Clean whitespace

    # If we find 'qa:result', start capturing and include the line
    if "qa:result" in line:
        capture = True
        keep_lines.append(line)

    # If capture mode is ON, keep all lines (including empty ones)
    elif capture:
        keep_lines.append(line)

    # If we reach '# end of answer', include it and stop capturing
    if "# end of answer" in line:
        keep_lines.append(line)
        capture = False  # Stop capturing

# Save the filtered output
with open(output_file_path, "w", encoding="utf-8") as outfile:
    outfile.write("\n".join(keep_lines))

print(f"Filtered lines saved to {output_file_path}")
