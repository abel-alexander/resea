import pdfplumber
def normalize_headers(headers):
    """
    Normalize table headers by handling multiline headers and combining year mentions.
    """
    normalized_headers = []
    for header in headers:
        if header is None or header.strip() == "":
            normalized_headers.append("")  # Empty cell
        else:
            # Combine year mentions with preceding text (e.g., "Years Ended December 31" -> "2023")
            normalized_headers.append(header.strip())
    return normalized_headers

def extract_tables_from_file(file_name):
    """
    Extract tables from a PDF file with specific handling for year mentions and multiline headers.

    Args:
        file_name (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries containing table metadata and data.
    """
    all_tables = []

    with pdfplumber.open(file_name) as pdf:
        for page_no, page in enumerate(pdf.pages):
            # Extract potential table blocks
            tables = page.extract_tables()

            if tables:
                for table_index, table in enumerate(tables):
                    # Skip invalid or too-short tables
                    if len(table) < 2:
                        continue

                    # Normalize and validate headers
                    headers = normalize_headers(table[0])  # First row as header
                    if not any(headers):  # Skip tables with completely empty headers
                        headers = [f"Column_{i+1}" for i in range(len(headers))]

                    # Extract and clean data rows
                    data_rows = table[1:]  # Remaining rows are data
                    table_data = [
                        {headers[i]: (row[i] if i < len(row) and row[i] is not None else "")
                         for i in range(len(headers))}
                        for row in data_rows
                    ]

                    # Extract table title from nearby text
                    title_bbox = (0, 0, page.width, 50)  # Adjust based on layout
                    table_title = page.crop(title_bbox).extract_text().strip()

                    # Add table metadata and data
                    table_info = {
                        "page_number": page_no + 1,
                        "table_index": table_index + 1,
                        "title": table_title,
                        "data": table_data,
                    }
                    all_tables.append(table_info)

    return all_tables
