def get_questions_and_answers_from_excel(section, excel_path='/path/to/your/questions.xlsx'):
    questions_df = pd.read_excel(excel_path)
    section_df = questions_df[['Q&A', section]].dropna()

    extracted_data = []

    for _, row in section_df.iterrows():
        company = row['Q&A']
        questions_answers = row[section].split('\n') if pd.notna(row[section]) else []

        for i in range(0, len(questions_answers), 2):
            question = questions_answers[i].strip()
            reference_answer = questions_answers[i+1].strip() if (i+1) < len(questions_answers) else ""
            if question and not question.startswith(('a.', 'b.', 'c.')):
                extracted_data.append({'Q&A': company, 'Section': section, 'Question': question, 'Reference Answer': reference_answer})
    
    return pd.DataFrame(extracted_data)
