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
