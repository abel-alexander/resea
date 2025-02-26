# Define input and output file paths
input_file = "path/to/your/input.txt"
output_file = "path/to/your/output.txt"

# Open the input file for reading and output file for writing
with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    inside_answer_block = False  # Flag to track if we are inside a QA answer block

    for line in infile:
        # Always preserve lines once inside the answer block
        if inside_answer_block:
            outfile.write(line)
            # Check if this line is the end of the answer block
            if "# end of answer" in line:
                inside_answer_block = False
            # Continue to next line (already written this one)
            continue

        # If we encounter the start of an answer block, enable capture mode
        if "qa:result:#Answer:" in line:
            inside_answer_block = True
            outfile.write(line)
            # (We will capture subsequent lines until "# end of answer" is found)
            continue

        # If the line contains 'qa:' (any other QA-related line), keep it
        if "qa:" in line:
            outfile.write(line)
            # (No flag change needed if it's not an answer block marker)
            continue

        # If none of the above conditions met, the line is not written (filtered out).
