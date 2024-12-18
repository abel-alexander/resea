import pdfplumber
import pandas as pd

def extract_tables_from_file(filename):
    """
    Extract tables and their metadata from a PDF file.

    Args:
        filename (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries containing table metadata and data.
    """
    def get_table_bboxes(page):
        """Get bounding boxes for tables."""
        return [table.bbox for table in page.find_tables()]

    def extract_titles_above_tables(page, table_bboxes):
        """Extract titles (lines) above each table."""
        titles = []
        for table_bbox in table_bboxes:
            title_bbox = (0, 0, page.width, table_bbox[1])  # Text above the table
            title_text = page.crop(title_bbox).extract_text()
            if title_text:
                lines = title_text.split('\n')[:5]  # Limit to top 5 lines
                title = next((line.strip() for line in lines if line.startswith("Table")), None)
                titles.append(title)
            else:
                titles.append("")  # No title found
        return titles

    # Initialize results
    all_tables = []

    # Open the PDF file
    with pdfplumber.open(filename) as pdf:
        for page_no, page in enumerate(pdf.pages):
            # Get table bounding boxes and titles
            table_bboxes = get_table_bboxes(page)
            titles = extract_titles_above_tables(page, table_bboxes)
            tables = page.extract_tables()

            # Process each table
            if tables:
                for table_index, table in enumerate(tables):
                    if not table or len(table) <= 1:  # Skip empty or invalid tables
                        continue

                    # Convert table to a DataFrame and clean
                    df = pd.DataFrame(table[1:], columns=table[0]).fillna("")
                    table_data = df.to_dict(orient='records')

                    # Add metadata for traceability
                    table_info = {
                        "page_number": page_no + 1,
                        "table_index": table_index + 1,
                        "title": titles[table_index] if table_index < len(titles) else f"Table_Page{page_no+1}_{table_index+1}",
                        "data": table_data
                    }
                    all_tables.append(table_info)
    
    return all_tables
