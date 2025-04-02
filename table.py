# === Imports ===
from pymupdf4llm import to_markdown
from typing import List
import traceback

# === Helper: Parse markdown table into list of dicts ===
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

# === Helper: Flatten parsed table to readable text block ===
def flatten_table_to_text(table_data: list) -> str:
    if not table_data:
        return ""
    headers = list(table_data[0].keys())
    rows = [headers] + [[row.get(h, "") for h in headers] for row in table_data]
    table_text = "\n".join([" | ".join(row) for row in rows])
    return f"Table Start\nTable Data:\n{table_text}\nTable End"

# === Main Function: Rectify only selected pages ===
def refine_plumber_tables_with_llm(
    file_name: str,
    tables: List[dict],
    llm_pipeline,
    rs1: List[dict]
):
    # 1. Collect unique table page numbers from plumber
    table_pages = sorted(set([table['page_number'] for table in tables]))

    # 2. Loop through each page, pull markdown, send to LLM
    for page_no in table_pages:
        try:
            md_text = to_markdown(file_name, pages=[page_no])
            if not md_text or not md_text[0].strip():
                print(f"⚠️ No markdown content found for page {page_no}")
                continue

            markdown_page_text = md_text[0].strip()

            # 3. Build prompt and run LLM
            prompt = f"""
Below is text extracted from page {page_no} of a financial PDF.
If there's a table in this text, reconstruct it cleanly as a markdown table.
If not, reply with "No table found".

{markdown_page_text}
"""
            response = llm_pipeline(
                prompt,
                temperature=0.7,
                max_new_tokens=1024,
                do_sample=False,
                return_full_text=False
            )
            llm_output = response[0]['generated_text'].strip()

            if "no table found" not in llm_output.lower():
                parsed_table = parse_markdown_table(llm_output)
                flattened = flatten_table_to_text(parsed_table)

                rs1.append({
                    'title': f'LLM-Rectified Table Page {page_no}',
                    'page_no': page_no,
                    'block_no_from': 0,
                    'block_no_to': 0,
                    'text': flattened
                })

        except Exception:
            print(f"⚠️ Error processing page {page_no}")
            traceback.print_exc()
