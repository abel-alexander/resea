import fitz  # PyMuPDF
from pathlib import Path
import json

# Import the new table extraction function
from table_extraction_module import extract_tables_from_file

def get_chunks(file_name):
    """
    Process a PDF file to extract text blocks and tables with metadata.

    Args:
        file_name (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries containing text blocks and table data.
    """
    tocs = pdf.get_toc(file_name, key=lambda x: x['id'], reverse=True)
    rs = []

    with fitz.open(file_name) as doc:
        for page_no in range(len(doc)):
            page = doc[page_no]
            title = get_title_from_page_no(tocs, page_no)

            # Existing block extraction
            blks = page.get_text("blocks")
            for blk in blks:
                rs.append({
                    'title': title,
                    'page_no': page_no,
                    'block_no_from': blk[5], 
                    'block_no_to': blk[6], 
                    'text': blk[4]
                })

    # ----------------------------
    # NEW: Table Extraction Step
    # ----------------------------
    # Extract tables from the file
    tables = extract_tables_from_file(file_name)  # New line: Call table extraction function
    
    # Append tables as blocks to the results
    for table in tables:  # New line: Iterate through extracted tables
        rs.append({
            'title': table['title'],           # Table title
            'page_no': table['page_number'],   # Page number
            'block_type': 'table',             # Block type as 'table'
            'table_data': table['data']        # Table data in JSON format
        })
    # ----------------------------

    # Existing merging logic
    rs1 = []
    for i in range(0, len(rs)):
        if rs1 and (rs1[-1]['text'][-1] in ['-', '_'] or rs1[-1]['text'][-1] not in ['.', '!', '?']):
            rs1[-1]['text'] += " " + rs[i]['text']
        else:
            rs1.append(rs[i].copy())

    rs2 = []
    for i in range(0, len(rs1)):
        rs2.append(rs1[i].copy())  # Append merged text blocks and tables

        # Splitting sentences in text blocks
        for sentence in split_text(rs1[i]['text']):
            temp = rs1[i].copy()
            temp['text'] = sentence
            rs2.append(temp)

    # Final metadata generation
    company_name = Path(file_name).stem
    add_processed_index = {'company_name': company_name, 'sourceRef': f"{file_name}"}
    json.dump({'processed': rs2}, open(f"{file_name}_output.json", 'w', encoding='utf-8'), indent=4)

    return rs2
