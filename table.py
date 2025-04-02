from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pymupdf4llm import to_markdown
from typing import List
import traceback

# === PromptTemplate setup ===
table_prompt = PromptTemplate(
    input_variables=["page_no", "page_text"],
    template="""
You are an expert at reading structured data from messy documents.

Below is text extracted from page {page_no} of a financial PDF.

If there is a table in the text, reconstruct it as a **clean markdown table only**.

Do not include explanations, commentary, or markdown syntax like triple backticks.

If no table is found, respond with exactly: No table found.

Text:
{page_text}
"""
)

# === LLMChain wrapper ===
def get_llm_chain(llm_pipeline):
    return LLMChain(llm=llm_pipeline, prompt=table_prompt)

# === Markdown table → list of dicts ===
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

# === Flatten list of dicts → readable markdown block ===
def flatten_table_to_text(table_data: list) -> str:
    if not table_data:
        return ""
    headers = list(table_data[0].keys())
    rows = [headers] + [[row.get(h, "") for h in headers] for row in table_data]
    table_text = "\n".join([" | ".join(row) for row in rows])
    return f"Table Start\nTable Data:\n{table_text}\nTable End"

# === Main function ===
def refine_plumber_tables_with_llm(file_name: str, tables: List[dict], llm_pipeline, rs1: List[dict]):
    table_pages = sorted(set([table['page_number'] for table in tables]))
    chain = get_llm_chain(llm_pipeline)

    for page_no in table_pages:
        try:
            md_text = to_markdown(file_name, pages=[page_no])
            if not md_text or not md_text[0].strip():
                print(f"⚠️ No markdown content found for page {page_no}")
                continue

            markdown_page_text = md_text[0].strip()

            # 🔍 Run the LLM via LangChain
            llm_output = chain.run({
                "page_no": page_no,
                "page_text": markdown_page_text
            }).strip()

            print(f"\n🔍 LLM Output for Page {page_no}:\n{llm_output}\n{'-'*60}")

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
