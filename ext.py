import os
import pandas as pd
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbeddings

# Define paths to folders containing documents
base_path = "/path/to/your/base/folder"
folders = ["Recent News", "Investor Presentation", "Equity Research", "10K", "Earnings Transcript", "Earnings Release"]

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

# Load questions from Excel
questions_df = pd.read_excel('/path/to/your/questions.xlsx', sheet_name=0, header=1)  # Adjust header and sheet_name as needed

# Function to get questions for a specific section and company
def get_questions(section, company):
    section_df = questions_df[questions_df.columns[questions_df.iloc[0] == section]]
    company_questions = section_df[section_df.iloc[:, 0] == company].dropna().values.flatten().tolist()
    questions = [q.split("\n")[0] for q in company_questions if isinstance(q, str)]
    answers = [q.split("\n")[1] if len(q.split("\n")) > 1 else "" for q in company_questions if isinstance(q, str)]
    return questions, answers

# Iterate over each folder
for folder in folders:
    folder_path = os.path.join(base_path, folder)
    output_folder = os.path.join(folder_path, "QA_results")
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate over each file in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):  # Assuming the documents are text files
            file_path = os.path.join(folder_path, file_name)
            company_name = os.path.splitext(file_name)[0]  # Extract company name from file name
            
            # Load the document
            documents = SimpleDirectoryReader(file_path).load_data()
            
            # Create index from document
            index = VectorStoreIndex.from_documents(documents, service_context=service_context)
            query_engine = index.as_query_engine()
            
            # Get questions and reference answers for the current section and company
            questions, reference_answers = get_questions(folder, company_name)
            
            # Open a file to write the QA results for this document
            result_file_name = f"{company_name}_qa_results.txt"
            result_file_path = os.path.join(output_folder, result_file_name)
            
            with open(result_file_path, 'w') as result_file:
                # Perform the queries for each document
                for question, ref_answer in zip(questions, reference_answers):
                    response = query_engine.query(question)
                    result_file.write(f"Question: {question}\n")
                    result_file.write(f"Reference Answer: {ref_answer}\n")
                    result_file.write(f"Response: {response}\n\n")
            
            print(f"QA results saved to {result_file_path}")
