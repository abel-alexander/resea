from langchain.prompts import PromptTemplate

table_prompt = PromptTemplate(
    input_variables=["page_no", "page_text"],
    template="""
You are an expert at recovering table data from messy markdown.

Below is text extracted from page {page_no} of a financial PDF.

Your task:
- Identify any content that visually resembles a table, even if misaligned or malformed.
- Reconstruct it into a clean markdown table using the `|` delimiter.
- Return ONLY markdown tables. Do not include any explanations, code blocks, or notes.
- If no table is found, return exactly: No table found.

Text:
{page_text}
"""
)
