
import pdfplumber

def extract_tables_from_file(file_name):
    """
    Extract tables from a PDF file and return them as JSON with metadata.
    """
    all_tables = []
    with pdfplumber.open(file_name) as pdf:
        for page_no, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                for table_index, table in enumerate(tables):
                    # Convert table into structured JSON
                    table_data = [dict(zip(table[0], row)) for row in table[1:] if len(row) == len(table[0])]
                    table_info = {
                        "page_number": page_no + 1,
                        "table_index": table_index + 1,
                        "title": f"Table_Page{page_no+1}_{table_index+1}",
                        "data": table_data
                    }
                    all_tables.append(table_info)
    return all_tables


def flatten_table_to_text(table_json):
    """
    Flattens table JSON into a readable text format preserving row-column structure.

    Args:
        table_json (list): The table data as JSON (list of dictionaries).

    Returns:
        str: Flattened table as text.
    """
    if not table_json or len(table_json) == 0:
        return "Empty Table"

    # Extract table headers
    headers = list(table_json[0].keys())
    rows = [headers]  # Start with headers

    # Add each row's values, converting None to empty string
    for row in table_json:
        row_values = [str(row.get(h, "") or "") for h in headers]  # Replace None with empty string
        rows.append(row_values)

    # Convert rows into readable text (Markdown-like format)
    table_text = "\n".join([" | ".join(row) for row in rows])
    return f"Table Data:\n{table_text}"



@st.cache_resource
def pdf_get_chunks(file_name):
    """
    Extract text blocks and tables (flattened as text) from a PDF file.

    Args:
        file_name (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries containing text blocks and flattened tables.
    """
    tocs = pdf_get_toc(file_name)
tocs.sort(key=lambda x: x['id'], reverse=True)
rs = []

with fitz.open(file_name) as doc:
    doc_title = doc.metadata['title']
    page_no = 0

    while page_no < len(doc):
        title, lvl = pdf_get_title_from_page_no(tocs, page_no+1)
        if lvl == 2 and title != doc_title:
            print(f"Title changed to: {title}")
            doc_title = title
            page_no -= 1

        print(f"Processing page {page_no+1}")
        blks = pdf_get_page_blocks(page)
        for blk in blks:
            blk_text = pdf_block_post_process_text(blk[4])
            rs.append({'title': title, 'page_no': page_no+1, 'block_no_from': blk[5], 'block_no_to': blk[6], 'text': blk_text})

        # Increment page number
        page_no += 1

# NEW: Extract tables and append to rs
tables = extract_tables_from_file(file_name)
for table in tables:
    flattened_text = "\n".join([" | ".join(map(str, row.values())) for row in table['data']])
    rs.append({
        'title': table['title'],
        'page_no': table['page_number'],
        'block_no_from': 0,  # No block range for tables
        'block_no_to': 0,
        'text': flattened_text  # Flattened table data as text
    })

# Existing logic to merge incomplete blocks
rs1 = []
for i in range(0, len(rs)):
    if rs1 and (rs1[-1]['text'][-1:] in ['-', '_'] or rs1[-1]['text'][-2:] in ['. ', '.\n']):
        rs1[-1]['text'] = rs1[-1]['text'][:-1] + ' ' + rs[i]['text']
    else:
        rs1.append(rs[i].copy())

# Split
rs2 = []
for i in range(0, len(rs1)):
    if len(rs1[i]['text']) > 0:
        rs2.append(rs1[i].copy())
        for sentence in split_text(rs1[i]['text']):
            temp = rs1[i].copy()
            temp['text'] = sentence
            rs2.append(temp)

company_name = Path(file_name).stem
add_processed_index = {'company_name': company_name, 'sourceRef': f"{{item['title']}}-Page{{item['page_no']}}-span{{item['block_no_from']}}-{{item['block_no_to']}}"}
json.dump({'processed': rs2}, open(f"{file_name}_output.json", 'w', encoding='utf-8'), indent=4)

return rs2

