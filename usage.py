def detect_and_extract_tables_with_mistral(extracted_text: List[str]) -> List[Dict]:
    """
    Uses Mistral (or another LLM) to detect and extract table data from extracted text.
    
    Parameters:
    - extracted_text: List of strings containing the raw text extracted from the PDF.

    Returns:
    - List of dictionaries where each dictionary represents a detected table with rows and headers.
    """
    from transformers import pipeline

    # Load a language model pipeline for text analysis
    table_detection_pipeline = pipeline("text-generation", model="mistral")  # Adjust the model as needed

    tables = []
    for page_text in extracted_text:
        prompt = f"""
        [TASK] Analyze the following text and extract any table-like structures. Return the tables in JSON format 
        with keys: "headers" (list of strings) and "rows" (list of lists of strings). Ignore other text.

        Text:
        {page_text}
        """
        
        response = table_detection_pipeline(prompt, max_length=2048, do_sample=False)
        try:
            table_data = eval(response[0]['generated_text'])  # Parse JSON-like response
            tables.append(table_data)
        except:
            print(f"Could not parse table data from text: {page_text[:100]}...")
            continue

    return tables


def tables_to_dataframes(tables: List[Dict]) -> List[pd.DataFrame]:
    """
    Converts extracted table dictionaries into pandas DataFrames.
    
    Parameters:
    - tables: List of dictionaries containing table headers and rows.

    Returns:
    - List of pandas DataFrames.
    """
    dataframes = []
    for table in tables:
        try:
            df = pd.DataFrame(table['rows'], columns=table['headers'])
            dataframes.append(df)
        except Exception as e:
            print(f"Error converting table to DataFrame: {e}")
            continue
    return dataframes


def process_pdf_and_extract_tables(pdf_path: str):
    """
    Full workflow to extract tables from a PDF, detect table structures using Mistral,
    and convert them into DataFrames.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    
    Returns:
    - List of pandas DataFrames, each representing a detected table.
    """
    # Step 1: Extract raw text from PDF (including paragraphs and tables)
    raw_text = extracted_data(pdf_path)  # Extracts all text from the PDF

    # Step 2: Use Mistral to detect and extract table data
    tables = detect_and_extract_tables_with_mistral(raw_text)

    # Step 3: Convert extracted table data into DataFrames
    dataframes = tables_to_dataframes(tables)

    return dataframes
