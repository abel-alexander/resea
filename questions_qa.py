import pandas as pd
import re

def clean_text(text):
    """Remove unwanted characters like tabs and question numbers."""
    text = text.replace('\t', '').strip()
    text = re.sub(r'^\d+\.\s*', '', text)  # Remove question numbers
    text = text.strip()
    return text

def get_questions_and_answers_from_excel(section, excel_path):
    questions_df = pd.read_excel(excel_path)
    section_df = questions_df[['Q&A', section]].dropna()

    extracted_data = []

    for _, row in section_df.iterrows():
        company = row['Q&A']
        questions_answers = row[section].split('\n') if pd.notna(row[section]) else []

        i = 0
        while i < len(questions_answers):
            question = clean_text(questions_answers[i])
            if question and not question.startswith('a.'):
                reference_answer = ""
                if (i + 1) < len(questions_answers):
                    answer_candidate = questions_answers[i + 1].strip()
                    if answer_candidate.startswith('a.'):
                        reference_answer = answer_candidate[2:].strip()  # Remove 'a.' prefix
                        i += 1  # Skip the answer line
                extracted_data.append({
                    'Company': company,
                    'Section': section,
                    'Question': question,
                    'Reference Answer': reference_answer
                })
            i += 1
    
    return pd.DataFrame(extracted_data)

# Example usage
excel_path = '/path/to/your/questions.xlsx'
section = 'Earnings Release'
qa_df = get_questions_and_answers_from_excel(section, excel_path)
qa_df
