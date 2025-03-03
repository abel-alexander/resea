import os

def get_reference_text(summary_root, company, section):
    """Retrieve the reference text from human summaries based on company and section name.
       Stops extracting when 'Q&A' is found."""
    section_path = os.path.join(summary_root, company, section)

    if not os.path.exists(section_path):
        print(f"Section '{section}' not found for company '{company}'.")
        return None

    # Find the first text file in the section folder
    text_files = [f for f in os.listdir(section_path) if f.endswith('.txt')]
    if not text_files:
        print(f"No reference text found in '{section}' for '{company}'.")
        return None

    text_file_path = os.path.join(section_path, text_files[0])

    with open(text_file_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Stop extracting at "Q&A"
    if "Q&A" in full_text:
        return full_text.split("Q&A")[0].strip()  # Return text before "Q&A"
    return full_text  # Return full text if "Q&A" is not found
