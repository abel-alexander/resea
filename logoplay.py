from langchain.prompts import PromptTemplate

table_prompt = PromptTemplate(
    input_variables=["page_no", "page_text"],
    template="""
You are an expert in financial data extraction.

Below is noisy text from page {page_no} of a financial report. It may contain line-based data or visual columns that do not follow markdown table formatting.

Your job is to:
- Identify any **repeated patterns or aligned values** that represent structured tabular data (even if the original table structure is missing).
- Reconstruct it as a **clean markdown table** using the `|` character to separate columns.
- If headers are missing, **infer them** from context (e.g., "Metric", "Current Period", "Previous Period").
- Return **only the markdown table** — no explanations, code blocks, or commentary.
- If nothing in the text resembles structured tabular data, return exactly: `No table found`

Text:
{page_text}
"""
)
