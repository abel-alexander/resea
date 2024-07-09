import os
import pandas as pd
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.readers.file import SimpleDirectoryReader
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
                    'Reference Answer': reference_answer,
                    'Response': ""  # Initialize the response column
                })
            i += 1
    
    return pd.DataFrame(extracted_data)

def perform_qa_for_section(section, base_path, excel_path):
    section_path = os.path.join(base_path, 'extracted_data', section)
    output_folder = os.path.join(base_path, "QA_results")
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Initialize LLM and embeddings
    llm = HuggingFaceLLM(
        context_window=4096,
        max_new_tokens=512,
        generate_kwargs={"temperature": 0.2, "do_sample": False},
        system_prompt="system-prompt",
        query_wrapper_prompt="query_wrapper_prompt",
        template_name="meta-llama/Llama-2-7b-chat-hf",
        model_name="meta-llama/Llama-2-7b-chat-hf",
        device_map="auto",
        model_kwargs={"torch_dtype": "torch.float16", "load_in_8bit": True}
    )
    
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    service_context = ServiceContext.from_defaults(chunk_size=1024, llm=llm, embed_model=embed_model)

    # Load questions and answers from Excel
    qa_df = get_questions_and_answers_from_excel(section, excel_path)

    # Process each company in qa_df
    for company_name in qa_df['Company'].unique():
        company_df = qa_df[qa_df['Company'] == company_name].copy()  # Work on a copy of the data
        
        # Construct the file path for the company's document
        file_path = os.path.join(section_path, f"{company_name}.txt")
        
        if not os.path.exists(file_path):
            print(f"File not found for company {company_name}: {file_path}")
            continue
        
        # Load the document using SimpleDirectoryReader
        reader = SimpleDirectoryReader(input_files=[file_path])
        documents = reader.load_data()
        
        # Create index from document
        index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        query_engine = index.as_query_engine()
        
        # Perform the queries and update the responses in the DataFrame
        for idx, row in company_df.iterrows():
            question = row['Question']
            response = query_engine.query(question)
            qa_df.loc[company_df.index[idx], 'Response'] = response
    
    # Save the updated DataFrame to a single Excel file
    result_file_path = os.path.join(output_folder, f"{section}_qa_results.xlsx")
    qa_df.to_excel(result_file_path, index=False)
    
    print(f"QA results saved to {result_file_path}")

# Example usage
perform_qa_for_section('Earnings Release', '/phoenix/workspaces/zk9zkma/Image_text_extraction', '/path/to/your/questions.xlsx')
