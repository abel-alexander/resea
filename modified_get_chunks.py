@st.cache_resource
def get_chunks(file_name):
    tocs = pdf.get_toc(file_name)
    tocs.sort(key=lambda x: x['id'], reverse=True)
    rs = []

    with fitz.open(file_name) as doc:
        for page_no in range(len(doc)):
            page = doc[page_no]
            title = get_title_from_page_no(tocs, page_no+1)

            if check_profile_name(title):
                ocr_text = convert_image_to_string(page)
                print(f"page was converted", file_name, title, ocr_text)
                rs.append({'title': title, 'page_no': page_no+1, 'block_no_from': 0, 'block_no_to': 0, 'text': ocr_text})
            else:
                blks = page.get_text("blocks")
                for blk in blks:
                    rs.append({'title': title, 'page_no': page_no+1, 
                               'block_no_from': blk[5], 'block_no_to': blk[6], 'text': blk[4]})

    # ----------------------------
    # NEW: Table Extraction Step
    # ----------------------------
    from table_extraction_module import extract_tables_from_file
    tables = extract_tables_from_file(file_name)  # Extract tables as JSON

    for table in tables:
        rs.append({
            'title': table['title'],            # Table title for consistency
            'page_no': table['page_number'],    # Page number
            'block_no_from': 0,                 # No block range for tables
            'block_no_to': 0,
            'text': json.dumps(table['data'])   # Store table data as JSON string
        })
    # ----------------------------

    rs1 = []
    # Merge incomplete blocks
    for i in range(0, len(rs)):
        if rs1 and (rs1[-1]['text'][-1:] in ['-', '_'] or rs1[-1]['text'][-2:] in ['. ', '.\n']):
            rs1[-1]['text'] = rs1[-1]['text'][:-1] + ' ' + rs[i]['text']
        elif len(rs1) > 1 and len(rs1[-1]['text']) > 200:
            rs1[len(rs1)-1]['text'] = rs1[-1]['text'] + '\n' + rs[i]['text']
        elif rs[len(rs1)-1]['text'][-1:] == ' ':
            rs1[len(rs1)-1]['block_no_to'] = rs1[-1]['block_no_to']
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
