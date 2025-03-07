from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["markdown_content"],
    template="""
    You are a highly precise AI trained to extract a structured Table of Contents (ToC) from text.

    **Instructions:**
    - **Only** extract the Table of Contents.
    - Do **not** include any explanations, introductions, or additional text.
    - **Do not** repeat the input text.
    - Preserve section numbering (e.g., `1, 1.1, i, ii, A, B`).
    - **Format the response in Markdown**.
    - **Return the output strictly between `<TOC_START>` and `<TOC_END>`**.

    ---
    **Here is the document:**
    ```
    {markdown_content}
    ```

    **Your response must follow this format:**
    ```
    <TOC_START>
    # Table of Contents

    - **1. Introduction**
    - **2. Financial Overview**
      - i. Revenue
      - ii. Expenses
    - **3. Market Analysis**
      - a. Competitor Landscape
      - b. Growth Opportunities
    <TOC_END>
    ```
    """
)
