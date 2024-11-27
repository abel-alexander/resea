import easyocr
import pandas as pd

def extract_text_from_pdf_with_easyocr(pdf_path, language="en"):
    """
    Extracts text and bounding box data from a PDF or image using EasyOCR.
    """
    reader = easyocr.Reader([language], gpu=False)
    results = reader.readtext(pdf_path, detail=1)  # Extract text with bounding boxes
    return results

def parse_table_from_ocr_results(ocr_results):
    """
    Attempts to structure OCR results into a table-like format.
    """
    # Filter OCR results and sort by bounding box y-coordinates (top to bottom)
    sorted_results = sorted(ocr_results, key=lambda x: x[0][0][1])

    rows = []
    for result in sorted_results:
        text = result[1].strip()
        rows.append(text.split())  # Split each detected text into words
    
    # Attempt to create a DataFrame from detected rows
    df = pd.DataFrame(rows)
    return df

def explain_table(df):
    """
    Converts a DataFrame into a descriptive paragraph explaining the table.
    """
    explanation = "The table contains the following data:\n\n"
    explanation += f"The table has {len(df)} rows and {len(df.columns)} columns. "
    
    for col in df.columns:
        column_values = df[col].tolist()
        explanation += f"Column {col + 1} contains values such as {', '.join(map(str, column_values[:3]))}, etc. "

    explanation += "The data is extracted from the provided PDF or image file."
    return explanation

# Running everything in a Jupyter Notebook cell
def run_ocr_pipeline(pdf_path):
    print("Step 1: Extracting text using OCR...")
    ocr_results = extract_text_from_pdf_with_easyocr(pdf_path)

    print("Step 2: Parsing table from OCR results...")
    table_df = parse_table_from_ocr_results(ocr_results)
    
    print("\nExtracted Table:")
    display(table_df)  # Display the table inline in the notebook

    print("\nStep 3: Generating table explanation...")
    table_explanation = explain_table(table_df)
    print("\nTable Explanation:")
    print(table_explanation)

# Example Usage
# Replace 'example.pdf' with the path to your PDF or image file
pdf_path = "example.pdf"  # Ensure this file is in the same directory or provide a full path
run_ocr_pipeline(pdf_path)
