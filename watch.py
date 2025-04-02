def extract_llm_tables_as_json(split_docs, llm_pipeline, temperature=0.7):
    tables = []
    for idx, chunk in enumerate(split_docs):
        page_num = chunk.metadata.get("page", idx + 1)
        prompt = f"""
The following text was extracted from a financial document. If any part of it looks like a table (even if broken), reconstruct it into a clean markdown table. If no table exists, reply with: No table found.

Text:
{chunk.page_content}
"""

        response = llm_pipeline(
            prompt,
            temperature=temperature,
            max_new_tokens=512,
            do_sample=False,
            return_full_text=False
        )

        llm_output = response[0]["generated_text"].strip()
        if is_valid_table(llm_output):
            try:
                parsed = parse_markdown_table(llm_output)
                tables.append({
                    "title": f"LLM-Detected Table Page {page_num}",
                    "page_number": page_num,
                    "data": parsed
                })
            except Exception as e:
                print(f"⚠️ Error parsing table on page {page_num}: {e}")
    return tables
