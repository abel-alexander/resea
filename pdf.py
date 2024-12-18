import re
import pdfplumber
import pandas as pd
import os
import json

def clear_previous_outputs(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?.,*)(=-]', '_', filename)
    sanitized = re.sub(r'\s+', '_', sanitized).replace('__', '_')
    return sanitized[:255]

def is_valid_header(row):
    """
    Check if a row contains valid headers like years, quarters, or other indicators.
    """
    pattern = re.compile(r"(20\d{2})|(\bQ\d{1,2}\b)|(\bFY\d{2,4}\b)|(\bIQ\d{1,2}A\b)", re.IGNORECASE)
    return any(pattern.search(str(cell)) for cell in row if cell)

def combine_multiline_headers(table):
    """
    Combine multi-line headers into a single header row.
    Args:
        table (list): Raw table extracted by pdfplumber.
    Returns:
        list: Table with combined headers.
    """
    if len(table) < 2:
        return table  # Not enough rows to combine
    
    header_row = table[0]
    for i in range(1, len(table)):
        if is_valid_header(table[i]):
            header_row = [f"{str(header_row[j]).strip()} {str(table[i][j]).strip()}".strip() 
                          if j < len(table[i]) else str(header_row[j]).strip() 
                          for j in range(len(header_row))]
        else:
            break  # Stop combining if no more headers are found
    return [header_row] + table[i:]  # Return combined header + remaining rows

def extract_and_fix_tables(pdf_path, output_json):
    """
    Extract tables from a PDF, combine multi-line headers, and save as JSON.
    Args:
        pdf_path (str): Path to the input PDF.
        output_json (str): Path to save the JSON output.
    """
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            tables = page.extract_tables({
                "vertical_strategy": "text",
                "horizontal_strategy": "lines",
                "snap_tolerance": 3
            })

            if tables:
                for table_index, table in enumerate(tables):
                    if not table or len(table) <= 1:
                        print(f"Skipping empty table on Page {page_number + 1}")
                        continue

                    # Combine multi-line headers
                    fixed_table = combine_multiline_headers(table)
                    df = pd.DataFrame(fixed_table[1:], columns=fixed_table[0])
                    df = df.dropna(how='all').fillna("")  # Clean up the table

                    # Ensure first column is treated as row labels
                    df.columns = ["Item"] + list(df.columns[1:])

                    # Append table information
                    table_data = df.to_dict(orient="records")
                    table_info = {
                        "page_number": page_number + 1,
                        "table_index": table_index + 1,
                        "title": f"Table_Page{page_number + 1}_{table_index + 1}",
                        "data": table_data
                    }
                    all_tables.append(table_info)

    # Save all tables to JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_tables, f, indent=4, ensure_ascii=False)
    print(f"Saved extracted tables to: {output_json}")

# Run the script
if __name__ == "__main__":
    pdf_path = "example.pdf"  # Replace with your PDF path
    output_json = "fixed_extracted_tables.json"

    extract_and_fix_tables(pdf_path, output_json)
