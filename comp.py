import re

# Define the input and output file paths
input_file_path = "usage.log"
output_file_path = "filtered_usage.log"

# Read the file and extract relevant lines
with open(input_file_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

keep_lines = []
capture = False

for line in lines:
    if "qa:" in line:
        keep_lines.append(line)
    elif "qa:result:#Answer:" in line:
        capture = True
        keep_lines.append(line)
    elif "# end of answer" in line:
        capture = False
        keep_lines.append(line)
    elif capture:
        keep_lines.append(line)

# Write the filtered lines to a new file
with open(output_file_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(keep_lines)

print(f"Filtered lines saved to {output_file_path}")
