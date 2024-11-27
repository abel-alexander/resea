import camelot
import os

def detect_tables_in_pdf(pdf_path, output_folder=None):
    """
    Detects tables in a PDF file using Camelot and optionally saves them as CSVs.
    
    Args:
        pdf_path (str): Path to the PDF file.
        output_folder (str, optional): Folder to save extracted tables as CSVs. If None, tables are not saved.
    
    Returns:
        tables (list): List of Camelot Table objects.
    """
    # Ensure the PDF file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file '{pdf_path}' does not exist.")
    
    print("Detecting tables in the PDF...")
    tables = camelot.read_pdf(pdf_path, pages="all")

    # Display table detection results
    print(f"Detected {len(tables)} tables.")
    for i, table in enumerate(tables):
        print(f"Table {i + 1} summary:")
        print(table.parsing_report)  # Show accuracy, whitespace, etc.
    
    # Optionally save tables to CSV
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        for i, table in enumerate(tables):
            csv_path = os.path.join(output_folder, f"table_{i + 1}.csv")
            table.to_csv(csv_path)
            print(f"Table {i + 1} saved to {csv_path}")
    
    return tables

# Example usage
if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "example.pdf"  # Replace with the path to your PDF file
    
    # Output folder to save detected tables as CSV files (optional)
    output_folder = "extracted_tables"

    # Detect and extract tables
    tables = detect_tables_in_pdf(pdf_path, output_folder)

    # Display the first few rows of each detected table
    for i, table in enumerate(tables):
        print(f"\nTable {i + 1}:")
        print(table.df.head())  # Display the first few rows of the table
