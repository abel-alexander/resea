from langchain.document_loaders import UnstructuredFileLoader
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import re

# === Settings ===
llm = pipeline("text-generation", model="meta-llama/Meta-Llama-3-8B-Instruct", device=0)  # Or your model
embedder = SentenceTransformer("all-mpnet-base-v2")
rs = []  # Final result block list

# === Helper Functions ===

def extract_table_with_llm(text: str) -> str:
    prompt = f"""
The following text was extracted from a financial document page. If any part of it looks like a table (even if broken), reconstruct it into a clean markdown table. If no table exists, reply with: No table found.

Text:
{text}

Reconstructed Table (if any):
"""
    result = llm(prompt, max_new_tokens=512, do_sample=False)[0]["generated_text"]
    return result.split("Reconstructed Table (if any):")[-1].strip()

def is_valid_table(llm_output: str) -> bool:
    return ("|" in llm_output and "---" in llm_output) or bool(re.search(r"\bYear\b.*\d{4}", llm_output))

def parse_markdown_table(markdown: str) -> list:
    lines = [line.strip() for line in markdown.strip().split("\n") if line.strip()]
    if len(lines) < 3:
        return []

    header = [h.strip() for h in lines[0].split("|") if h.strip()]
    data_rows = []

    for row in lines[2:]:  # skip header + separator
        cells = [c.strip() for c in row.split("|") if c.strip()]
        if len(cells) == len(header):
            data_rows.append(dict(zip(header, cells)))
    return data_rows

def flatten_table_to_text(table_data: list) -> str:
    if not table_data:
        return ""

    headers = list(table_data[0].keys())
    rows = [headers] + [[row.get(h, "") for h in headers] for row in table_data]

    # Convert rows into readable text (Markdown-like format)
    table_text = "\n".join([" | ".join(row) for row in rows])
    return f"Table Start\nTable Data:\n{table_text}\nTable End"

# === Main Pipeline ===

def extract_llm_tables_to_rs(file_name: str):
    loader = UnstructuredFileLoader(file_name)
    docs = loader.load()

    for idx, doc in enumerate(docs):
        page_num = doc.metadata.get("page", idx + 1)
        llm_output = extract_table_with_llm(doc.page_content)

        if is_valid_table(llm_output):
            try:
                structured_data = parse_markdown_table(llm_output)
                flattened_text = flatten_table_to_text(structured_data)

                rs.append({
                    'title': f'LLM-Detected Table Page {page_num}',
                    'page_no': page_num,
                    'block_no_from': 0,
                    'block_no_to': 0,
                    'text': flattened_text
                })

            except Exception as e:
                print(f"⚠️ Error parsing table on page {page_num}: {e}")

    return rs
