import easyocr
import pandas as pd
import cv2
from matplotlib import pyplot as plt

def extract_text_from_pdf_with_easyocr(pdf_path, language="en"):
    """
    Extracts text and bounding box data from a PDF or image using EasyOCR.
    """
    reader = easyocr.Reader([language], gpu=False)
    results = reader.readtext(pdf_path, detail=1)  # Extract with bounding boxes
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

def visualize_ocr_results(pdf_path, ocr_results):
    """
    Visualizes OCR results on the provided PDF or image for debugging.
    """
    image = cv2.imread(pdf_path)
    for result in ocr_results:
        bbox, text, _ = result
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title("OCR Results Visualization")
    plt.show()

# Running everything in a Jupyter Notebook cell
def run_ocr_pipeline(pdf_path):
    print("Step 1: Extracting text using OCR...")
    ocr_results = extract_text_from_pdf_with_easyocr(pdf_path)

    print("Step 2: Visualizing OCR results...")
    visualize_ocr_results(pdf_path, ocr_results)

    print("Step 3: Parsing table from OCR results...")
    table_df = parse_table_from_ocr_results(ocr_results)
    
    print("\nExtracted Table:")
    display(table_df)  # Display the table inline in the notebook

    print("\nStep 4: Generating table explanation...")
    table_explanation = explain_table(table_df)
    print("\nTable Explanation:")
    print(table_explanation)

# Example Usage
# Replace 'example.pdf' with the path to your PDF or image file
pdf_path = "example.pdf"  # Ensure this file is in the same directory or provide a full path
run_ocr_pipeline(pdf_path)
