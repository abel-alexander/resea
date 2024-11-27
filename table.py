from transformers import pipeline
import pdfplumber

# Initialize the Hugging Face model pipeline
def initialize_model(model_name="meta-llama/Llama-2-8b-chat-hf"):
    instruct_pipeline = pipeline(
        "text-generation",
        model=model_name,
        device=0  # Use 0 for GPU, -1 for CPU
    )
    return instruct_pipeline

# Function to extract tables from a PDF using pdfplumber
def extract_tables_from_pdf(pdf_path):
    tables_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()  # Extract tables from each page
            for idx, table in enumerate(tables):
                formatted_table = {
                    "page": page_num,
                    "table_index": idx + 1,
                    "data": table
                }
                tables_data.append(formatted_table)
    return tables_data

# Prepare the LLM prompt for table extraction
def prepare_prompt(table, page, table_index):
    prompt = (
        f"Extract and format the following table from a PDF:\n\n"
        f"Page {page}, Table {table_index}:\n"
        f"{table}\n\n"
        f"Please format this table as a clean Markdown table or CSV format."
    )
    return prompt

# Process tables using the LLM
def process_tables_with_llm(tables_data, instruct_pipeline):
    formatted_tables = []
    for table_info in tables_data:
        page = table_info["page"]
        table_index = table_info["table_index"]
        table_data = table_info["data"]
        if not table_data:
            continue  # Skip empty tables
        
        # Convert table data to a string
        table_as_string = "\n".join([", ".join(map(str, row)) for row in table_data])
        prompt = prepare_prompt(table_as_string, page, table_index)
        
        # Generate output using the model
        response = instruct_pipeline(prompt, max_length=512)
        formatted_tables.append({
            "page": page,
            "table_index": table_index,
            "formatted_table": response[0]["generated_text"]
        })
    return formatted_tables

# Main function to handle PDF table extraction and processing
def extract_and_format_tables(pdf_path):
    model = initialize_model()
    tables_data = extract_tables_from_pdf(pdf_path)
    formatted_tables = process_tables_with_llm(tables_data, model)
    
    # Output results
    for table in formatted_tables:
        print(f"Page {table['page']}, Table {table['table_index']}:\n")
        print(table["formatted_table"])
        print("\n" + "="*80 + "\n")

# Usage
pdf_path = "example.pdf"  # Replace with your PDF file path
extract_and_format_tables(pdf_path)
