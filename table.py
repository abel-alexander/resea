# === Helper: Convert markdown table (string) to structured list of dicts ===
def parse_markdown_table(markdown: str) -> list:
    lines = [line.strip() for line in markdown.strip().split("\n") if line.strip()]
    if len(lines) < 3:
        return []

    header = [h.strip() for h in lines[0].split("|") if h.strip()]
    data_rows = []
    for row in lines[2:]:
        cells = [c.strip() for c in row.split("|") if c.strip()]
        if len(cells) == len(header):
            data_rows.append(dict(zip(header, cells)))
    return data_rows

# === Helper: Flatten parsed table to text for rs1 block ===
def flatten_table_to_text(table_data: list) -> str:
    if not table_data:
        return ""
    headers = list(table_data[0].keys())
    rows = [headers] + [[row.get(h, "") for h in headers] for row in table_data]
    table_text = "\n".join([" | ".join(row) for row in rows])
    return f"Table Start\nTable Data:\n{table_text}\nTable End"

# === LLM Extractor: Clean up a markdown block from one page ===
def extract_and_structure_table_from_page(doc, llm_pipeline, temperature=0.7):
    page_no = doc.metadata.get("page", 0)
    prompt = f"""
Below is text extracted from page {page_no} of a financial PDF.
If there's a table in this text, reconstruct it cleanly as a markdown table.
If not, reply with "No table found".

{doc.page_content}
"""
    response = llm_pipeline(
        prompt,
        temperature=temperature,
        max_new_tokens=1024,
        do_sample=False,
        return_full_text=False
    )
    return response[0]['generated_text'].strip()

# === Master function: Use table page numbers from plumber, clean with LLM ===
def refine_plumber_tables_with_llm(file_name, tables, llm_pipeline, rs1):
    from pymupdf4llm import PyMuPDFLoader

    # 1. Collect table page numbers from plumber
    table_pages = sorted(set([table['page_number'] for table in tables]))

    # 2. Extract clean markdown per page using pymupdf4llm
    loader = PyMuPDFLoader(file_name)
    page_docs = loader.load(page_chunks=True)

    # 3. Filter only the pages where tables were found
    target_docs = [doc for doc in page_docs if doc.metadata["page"] in table_pages]

    # 4. Send those pages to LLM for table reconstruction
    for doc in target_docs:
        page_no = doc.metadata["page"]
        raw_markdown = extract_and_structure_table_from_page(doc, llm_pipeline)

        if "no table found" not in raw_markdown.lower():
            try:
                parsed_table = parse_markdown_table(raw_markdown)
                flattened = flatten_table_to_text(parsed_table)

                rs1.append({
                    'title': f'LLM-Rectified Table Page {page_no}',
                    'page_no': page_no,
                    'block_no_from': 0,
                    'block_no_to': 0,
                    'text': flattened
                })

            except Exception as e:
                print(f"⚠️ Failed to parse table on page {page_no}: {e}")
