def extract_inference_lines_with_timestamp(log_file_path):
    inference_data = []

    # Define unwanted names (case insensitive)
    unwanted_names = {"kenny", "anita", "abel", "richa"}

    # Timestamp pattern (YYYY-MM-DD HH:MM:SS,XXX)
    timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

    # Email and inference pattern
    inference_pattern = re.compile(r'([\w\.-]+@[\w\.-]+).*?inference:result:\s*(.+)', re.IGNORECASE)

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Detect timestamp
            timestamp_match = timestamp_pattern.match(line)

            # Detect inference result line
            inference_match = inference_pattern.search(line)
            if timestamp_match and inference_match:
                timestamp = timestamp_match.group(1)
                email = inference_match.group(1)
                answer = inference_match.group(2).strip()

                # Skip if the email contains an unwanted name
                if any(name in email.lower() for name in unwanted_names):
                    continue

                inference_data.append([timestamp, email, answer])

    # Convert to DataFrame
    df_inference = pd.DataFrame(inference_data, columns=["Timestamp", "Email", "Answer"])
    return df_inference

# Usage
df_inference = extract_inference_lines_with_timestamp(log_file_path)

# Display extracted data
tools.display_dataframe_to_user(name="Filtered Inference Answers", dataframe=df_inference)
