import easyocr
import pandas as pd
import cv2
# from matplotlib import pyplot as plt


def extract_text_from_pdf_with_easyocr(pdf_path, language="en"):
    """
    Extracts text and bounding box data from a PDF using EasyOCR.
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

    explanation += "The data is extracted from the provided PDF file."
    return explanation


# def visualize_pdf_text(pdf_path, ocr_results):
#     """
#     Visualize OCR results on the PDF for debugging purposes.
#     """
#     image = cv2.imread(pdf_path)
#     for result in ocr_results:
#         bbox, text, _ = result
#         (top_left, top_right, bottom_right, bottom_left) = bbox
#         top_left = tuple(map(int, top_left))
#         bottom_right = tuple(map(int, bottom_right))
#         cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
#         cv2.putText(image, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
#
#     plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     plt.show()


if __name__ == "__main__":
    # Path to your PDF or image file
    pdf_path = "pib1.pdf"

    # Extract text and bounding boxes using OCR
    print("Extracting text using OCR...")
    ocr_results = extract_text_from_pdf_with_easyocr(pdf_path)

    # Visualize the OCR results (optional, for debugging)
    # visualize_pdf_text(pdf_path, ocr_results)

    # Parse OCR results into a structured table
    print("Parsing table from OCR results...")
    table_df = parse_table_from_ocr_results(ocr_results)

    # Display the extracted table
    print("\nExtracted Table:")
    print(table_df)

    # Generate a paragraph explaining the table
    print("\nGenerating explanation...")
    table_explanation = explain_table(table_df)
    print("\nTable Explanation:")
    print(table_explanation)
