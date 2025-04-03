table_prompt = PromptTemplate(
    input_variables=["page_no", "page_text"],
    template="""
You are an expert data cleaning assistant.

The following text was extracted from page {page_no} of a financial report. It contains line-by-line structured data, not in table format.

Your task:
- Identify all lines that follow a "label: value" or "label    value" pattern.
- Reformat only that information into a markdown table using `|` to separate columns.
- Use the label as the first column, and value as the second column.
- Do not hallucinate or guess missing values or columns.
- Do not add additional rows, headers, or formatting beyond what’s already in the text.
- Preserve the original values exactly.
- If no such lines exist, return exactly: No table found.

Text:
{page_text}
"""
)
