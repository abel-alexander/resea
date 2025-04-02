# === Convert raw table to markdown string ===
def table_data_to_markdown(data: list[list]) -> str:
    if not data or len(data) < 2:
        return ""
    header = data[0]
    rows = data[1:]
    lines = [" | ".join(header), " | ".join(["---"] * len(header))]
    for row in rows:
        if len(row) == len(header):
            lines.append(" | ".join(row))
    return "\n".join(lines)

# === Rectify markdown table using LLM ===
def rectify_table_with_llm(markdown_table: str, llm_pipeline, temperature=0.7, max_new_tokens=512) -> str:
    prompt = f"""
Below is a possibly broken markdown table extracted from a PDF. Please clean it up — fix misalignments, merged cells, or formatting issues, and return a corrected markdown table.

Original Table:
{markdown_table}
"""
    response = llm_pipeline(
        prompt,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        return_full_text=False
    )
    return response[0]["generated_text"].strip()

# === Parse markdown table into list of dicts ===
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

# === Flatten table into readable markdown-style block ===
def flatten_table_to_text(table_data: list) -> str:
    if not table_data:
        return ""
    headers = list(table_data[0].keys())
    rows = [headers] + [[row.get(h, "") for h in headers] for row in table_data]
    table_text = "\n".join([" | ".join(row) for row in rows])
    return f"Table Start\nTable Data:\n{table_text}\nTable End"

# === Main loop to process and append to rs1 ===
def process_plumber_tables_with_llm(tables: list, llm_pipeline, rs1: list):
    for table in tables:
        markdown = table_data_to_markdown(table['data'])
        fixed_markdown = rectify_table_with_llm(markdown, llm_pipeline)
        parsed_table = parse_markdown_table(fixed_markdown)
        flattened_text = flatten_table_to_text(parsed_table)

        rs1.append({
            'title': table['title'],
            'page_no': table['page_number'],
            'block_no_from': 0,
            'block_no_to': 0,
            'text': flattened_text
        })
