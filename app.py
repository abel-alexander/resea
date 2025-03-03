import os

def get_human_summary(summary_root, company, section):
    """Retrieve human summary text based on company and section name."""
    section_path = os.path.join(summary_root, company, section)

    # Ensure section folder exists
    if not os.path.exists(section_path):
        print(f"Section '{section}' not found for company '{company}'.")
        return None

    # Find the first text file inside the section folder
    text_files = [f for f in os.listdir(section_path) if f.endswith('.txt')]
    if not text_files:
        print(f"No summaries found in '{section}' of '{company}'.")
        return None

    text_file_path = os.path.join(section_path, text_files[0])  # Process the first found file

    with open(text_file_path, "r", encoding="utf-8") as f:
        return f.read()

# Set the root directory for human summaries
summary_root = "/GCMTechAnalytics/docs/banker test/Human/Human Summaries"  # Adjust as needed

# Modify the loop in your script
for t in toc:
    lvl = t['lvl']
    sname = t['title']
    
    # Extract company name from file_name (assuming file_name is like "microsoft.pdf")
    company_name = os.path.basename(file_name).replace('.pdf', '').capitalize()  

    # Get text from human summary
    txt = get_human_summary(summary_root, company_name, sname)

    if txt is None:
        continue  # Skip processing if no summary found

    st.markdown(sname)
    result = mistral.process_section('@', sname, txt)
    col_sum, col_score = st.columns([6,4])

    with col_sum:
        st.markdown(result)
    
    with col_score:
        score = evaluate_summary(txt, result)
        st.markdown(score)
