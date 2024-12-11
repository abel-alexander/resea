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







from pypdf import PdfReader
import pandas as pd
import re

def extract_text_from_pdf(pdf_path: str) -> list:
    """
    Extracts raw text from a PDF file using PyPDF.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    
    Returns:
    - List of strings, where each string is the text of a single page.
    """
    reader = PdfReader(pdf_path)
    return [page.extract_text() for page in reader.pages]

def detect_table_like_text(page_text: str) -> list:
    """
    Detects table-like text patterns in a given page text.
    
    Parameters:
    - page_text: The raw text of a PDF page.
    
    Returns:
    - List of strings, where each string is a detected table-like structure.
    """
    tables = []
    lines = page_text.splitlines()
    table_lines = []
    
    for line in lines:
        # Heuristic: Lines with delimiters like `|`, `,`, or consistent whitespace
        if re.search(r'[|,\t]', line) or len(re.findall(r'\s{2,}', line)) > 2:
            table_lines.append(line)
        elif table_lines:
            # End of a table block
            tables.append("\n".join(table_lines))
            table_lines = []
    
    if table_lines:
        tables.append("\n".join(table_lines))  # Add last table if it ends at the end of the page
    
    return tables

def parse_table_to_dataframe(table_text: str) -> pd.DataFrame:
    """
    Parses table-like text into a pandas DataFrame.
    
    Parameters:
    - table_text: The text of a detected table.
    
    Returns:
    - A pandas DataFrame representing the table.
    """
    # Split lines and parse columns
    lines = table_text.splitlines()
    data = [re.split(r'[|,\t]', line.strip()) for line in lines if line.strip()]
    
    # Use the first row as the header if it looks like column names
    if all(re.match(r'[a-zA-Z0-9]', col) for col in data[0]):
        headers = data[0]
        rows = data[1:]
    else:
        headers = [f"Column {i+1}" for i in range(len(data[0]))]
        rows = data
    
    return pd.DataFrame(rows, columns=headers)

def extract_tables_from_pdf(pdf_path: str) -> list:
    """
    Extracts tables from a PDF file and converts them into pandas DataFrames.
    
    Parameters:
    - pdf_path: Path to the PDF file.
    
    Returns:
    - List of pandas DataFrames, each representing a detected table.
    """
    pages = extract_text_from_pdf(pdf_path)
    all_tables = []

    for page_text in pages:
        table_texts = detect_table_like_text(page_text)
        for table_text in table_texts:
            try:
                df = parse_table_to_dataframe(table_text)
                all_tables.append(df)
            except Exception as e:
                print(f"Error parsing table: {e}")
    
    return all_tables
