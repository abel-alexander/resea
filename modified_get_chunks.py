@st.cache_resource
def pdf_get_chunks(file_name):
    """
    Extract text blocks and tables (flattened as text) from a PDF file.

    Args:
        file_name (str): Path to the PDF file.

    Returns:
        list: A list of dictionaries containing text blocks and flattened tables.
    """
    # Fetch Table of Contents (TOC) and sort locally
    tocs = pdf_get_toc(file_name)
    tocs.sort(key=lambda x: x['id'], reverse=True)

    rs = []

    # Extract text blocks
    with fitz.open(file_name) as doc:
        for page_no in range(len(doc)):
            page = doc[page_no]
            title = get_title_from_page_no(tocs, page_no + 1)

            # OCR text extraction
            if check_profile_name(title):
                ocr_text = convert_image_to_string(page)
                rs.append({
                    'title': title,
                    'page_no': page_no + 1,
                    'block_no_from': 0,
                    'block_no_to': 0,
                    'text': ocr_text
                })
            else:
                # Text blocks extraction
                blks = page.get_text("blocks")
                for blk in blks:
                    rs.append({
                        'title': title,
                        'page_no': page_no + 1,
                        'block_no_from': blk[5],
                        'block_no_to': blk[6],
                        'text': blk[4]
                    })

    # ----------------------------
    # NEW: Table Extraction and Flattening
    # ----------------------------
    tables = extract_tables_from_file(file_name)  # Extract tables as JSON
    for table in tables:
        flattened_text = flatten_table_to_text(table['data'])  # Flatten the table into structured text
        rs.append({
            'title': table['title'],
            'page_no': table['page_number'],
            'block_no_from': 0,
            'block_no_to': 0,
            'text': flattened_text  # Append flattened table text
        })

    # ----------------------------
    # Existing Logic: Merge Incomplete Blocks
    # ----------------------------
    rs1 = []
    for i in range(0, len(rs)):
        if 'text' not in rs[i]:  # Skip entries without 'text'
            rs1.append(rs[i].copy())
            continue

        if rs1 and (rs1[-1]['text'][-1:] in ['-', '_'] or rs1[-1]['text'][-2:] in ['. ', '.\n']):
            rs1[-1]['text'] = rs1[-1]['text'][:-1] + ' ' + rs[i]['text']
        else:
            rs1.append(rs[i].copy())

    # ----------------------------
    # Final Split Logic
    # ----------------------------
    rs2 = []
    for i in range(0, len(rs1)):
        if len(rs1[i]['text']) > 0:
            rs2.append(rs1[i].copy())
            for sentence in split_text(rs1[i]['text']):
                temp = rs1[i].copy()
                temp['text'] = sentence
                rs2.append(temp)

    # Return processed chunks
    return rs2
