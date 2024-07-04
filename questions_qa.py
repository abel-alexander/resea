# Function to load questions and reference answers from the specified section and company
def get_questions_from_excel(section, excel_path='/path/to/your/questions.xlsx'):
    questions_df = pd.read_excel(excel_path)
    questions_df = questions_df[['Q&A', section]].dropna()
    
    extracted_questions = []
    
    for _, row in questions_df.iterrows():
        company = row['Q&A']
        questions_and_answers = row[section].split('\n') if pd.notna(row[section]) else []
        
        for qa in questions_and_answers:
            if qa.strip() and not qa.strip().startswith(('a.', 'b.', 'c.')):
                # Split question and answer
                question = qa.split('\t')[0].strip()
                answer = '\t'.join(qa.split('\t')[1:]).strip() if '\t' in qa else ''
                extracted_questions.append({'Company': company, 'Section': section, 'Question': question, 'Reference Answer': answer})
    
    return pd.DataFrame(extracted_questions)
