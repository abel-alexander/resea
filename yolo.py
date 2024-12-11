import os
from tabula import read_pdf
import pandas as pd

# Function to extract tables from a range of PDF pages using Tabula
def extract_tables_with_tabula(pdf_path, start_page, end_page, output_dir):
    all_tables = []

    for page_number in range(start_page, end_page + 1):
        print(f"Processing page {page_number}...")
        tables = read_pdf(pdf_path, pages=page_number, multiple_tables=True, pandas_options={'header': None})
        
        if tables:
            for i, table in enumerate(tables):
                output_file = os.path.join(output_dir, f"table_page_{page_number}_table_{i + 1}.csv")
                table.to_csv(output_file, index=False)
                print(f"Extracted table saved to {output_file}")
                all_tables.append(table)
        else:
            print(f"No tables found on page {page_number}.")

    return all_tables

# Main Script
def main():
    pdf_path = input("Enter the path to the PDF: ")
    start_page = int(input("Enter the starting page number: "))
    end_page = int(input("Enter the ending page number: "))
    output_dir = input("Enter the directory to save extracted tables: ")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract tables from the specified page range
    tables = extract_tables_with_tabula(pdf_path, start_page, end_page, output_dir)

    print(f"Extraction completed. {len(tables)} tables found and saved.")

if __name__ == "__main__":
    main()
