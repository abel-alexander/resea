def get_questions_from_excel(section, excel_path='/path/to/your/questions.xlsx'):
    questions_df = pd.read_excel(excel_path)
    questions_df = questions_df[['Q&A', section]].dropna()
    
    extracted_questions = []
    
    for _, row in questions_df.iterrows():
        company = row['Q&A']
        questions = row[section].split('\n') if pd.notna(row[section]) else []
        
        for q in questions:
            if q.strip() and not q.strip().startswith(('a.', 'b.', 'c.')):
                extracted_questions.append({'Company': company, 'Section': section, 'Question': q.strip()})
    
    return pd.DataFrame(extracted_questions)
