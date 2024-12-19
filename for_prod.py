def get_chunks(file_name):
    tocs = pdf_get_toc(file_name)
    tocs.sort(key=lambda x: x['id'], reverse=True)
    rs = []
    
    with fitz.open(file_name) as doc:
        doctitle = doc.metadata['title']
        page_no = 0
    
        while page_no < len(doc):
            title, lvl = pdf_toc.get_title_from_page_no(tocs, page_no + 1)
            if lvl == 2 and pdf_toc.is_page_dnd(page):
                print(f"skip page: {page_no+1} onwards")
                while page_no + 1 < len(doc):
                    page_no = page_no + 1
                    new_title, new_lvl = pdf_toc.get_title_from_page_no(tocs, page_no + 1)
                    if new_title == title:
                        # Change of title
                        if title == 'Deutsche Bank':
                            # Processing the last page
                            page_no = page_no + 1
                        page_no = doc[page_no]
                        break
                print(f"skip resume page: {page_no+1}")
            blks = pdf_toc.get_page_blocks(page)
            for blk in blks:
                blk_text = pdf_toc.post_process_text(blk[4])
                if len(blk_text) > 0:
                    rs.append({
                        'title': title,
                        'page_no': page_no + 1,
                        'block_no_from': blk[5],
                        'block_no_to': blk[5],
                        'text': blk_text
                    })
    
            # Increment page number
            page_no += 1

    # NEW: Extract tables and append to rs
    tables = extract_tables_from_file(file_name)  # Extract tables as JSON
    for table in tables:
        flattened_text = "\n".join([" | ".join(map(str, row.values())) for row in table['data']])
        rs.append({
            'title': table['title'],
            'page_no': table['page_number'],
            'block_no_from': 0,  # No block range for tables
            'block_no_to': 0,
            'text': flattened_text  # Flattened table data as text
        })
    
    # Handle incomplete blocks
    rs1 = []
    for i in range(0, len(rs)):
        if i == 0:
            rs1.append(rs[i].copy())
        elif rs1[len(rs1)-1]['text'][-2:] == "-\n" or rs1[len(rs1)-1]['text'][-2:] == "\n":
            rs1[len(rs1)-1]['text'] = rs1[len(rs1)-1]['text'][:-1] + rs[i]['text']
            rs1[len(rs1)-1]['block_no_to'] = rs[i]['block_no_to']
        elif len(rs1[len(rs1)-1]['text']) < 200:
            rs1[len(rs1)-1]['text'] += rs[i]['text']
            rs1[len(rs1)-1]['block_no_to'] = rs[i]['block_no_to']
        else:
            rs1.append(rs[i].copy())
    
    # Split into smaller chunks
    rs2 = []
    for i in range(0, len(rs1)):
        if i == 0:
            rs2.append(rs1[i].copy())
        else:
            for sentence in split_text(rs1[i]['text']):
                temp = rs1[i].copy()
                temp['text'] = sentence
                rs2.append(temp)
    
    # Add document metadata
    company_name = Path(file_name).stem
    for item in rs2:
        item['text'] = f"\n---\ncompany name: '{company_name} '\nSourceRef:'{item['title']}-Page: {item['page_no']}-ispn-{item['page_no']}-{item['block_no_from']}-{item['block_no_to']}-ispn'\ntext:\n{item['text']}\n---\n"
    return rs2
