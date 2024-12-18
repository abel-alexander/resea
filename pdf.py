import re
import pdfplumber
import pandas as pd
import os
import shutil
import json

def clear_previous_outputs(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?.,*)(=-]', '_', filename)
    sanitized = re.sub(r'\s+', '_', sanitized).replace('__', '_')
    return sanitized[:255]

def extract_text_within_bbox(page, bbox):
    return page.within_bbox(bbox).extract_text()

def get_table_bboxes(page):
    return [table.bbox for table in page.find_tables()]

def extract_titles_above_tables(page, table_bboxes):
    titles = []
    for table_bbox in table_bboxes:
        title_bbox = (0, 0, page.width, table_bbox[1])  # Text above the table
        title_text = extract_text_within_bbox(page, title_bbox)
        if title_text:
            lines = title_text.split('\n')[:5]  # Limit to top 5 lines
            title = next((line.strip() for line in lines if line.startswith("Table")), None)
            if title:
                titles.append(title)
    return titles

def clean_table_headers_and_fix_items(df):
    """
    Clean table headers and ensure the first column is treated as row labels (Item).
    Args:
        df (pd.DataFrame): Extracted table as a DataFrame.
    Returns:
        pd.DataFrame: Cleaned table with "Item" as row labels.
    """
    if not df.empty:
        # Promote the first column as "Item" (row headers)
        new_columns = ["Item"] + [str(col).strip() if col else f"Column_{i}" for i, col in enumerate(df.columns[1:], start=1)]
        df.columns = new_columns
        return df.reset_index(drop=True)
    return df

def extract_tables_to_json(pdf_path, output_file, pages=None):
    """
    Extract tables and titles from a PDF and save as a structured JSON file.
    Args:
        pdf_path (str): Path to the input PDF file.
        output_file (str): Path to save the JSON output.
        pages (list): Optional list of page numbers to process.
    """
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        pages = pages or range(len(pdf.pages))  # Default to all pages
        for page_number in pages:
            page = pdf.pages[page_number]
            table_bboxes = get_table_bboxes(page)
            titles = extract_titles_above_tables(page, table_bboxes)
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

                    # Convert to DataFrame and fix headers
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.dropna(how="all").fillna("")  # Clean empty rows and missing values
                    df = clean_table_headers_and_fix_items(df)  # Fix row labels

                    # Convert to JSON-friendly structure
                    table_data = df.to_dict(orient="records")

                    # Prepare table metadata
                    table_info = {
                        "page_number": page_number + 1,
                        "table_index": table_index + 1,
                        "title": titles[table_index] if table_index < len(titles) else f"Table_Page{page_number + 1}_{table_index + 1}",
                        "data": table_data
                    }
                    all_tables.append(table_info)

    # Save all tables to JSON
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_tables, json_file, indent=4, ensure_ascii=False)
    print(f"Saved extracted tables to: {output_file}")

# Run the script
pdf_path = "example.pdf"  # Replace with your PDF file path
output_json = "extracted_tables.json"

# Clear outputs and extract tables
clear_previous_outputs("temp_outputs")
extract_tables_to_json(pdf_path, output_json)
