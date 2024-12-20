# Add document metadata
company_name = Path(file_name).stem
for item in rs2:
    # Custom SourceRef logic for tables and text
    if "Table Start" in item['text']:
        # For tables
        item['text'] = f"""
        ---
        company name: '{company_name}'
        SourceRef: '{item['title']}-Page: {item['page_no']}-TableIndex: {item.get('table_index', 'N/A')}'
        text:
        {item['text']}
        ---
        """
    else:
        # For text blocks
        item['text'] = f"""
        ---
        company name: '{company_name}'
        SourceRef: '{item['title']}-Page: {item['page_no']}-ispn-{item['page_no']}-{item['block_no_from']}-{item['block_no_to']}-ispn'
        text:
        {item['text']}
        ---
        """
