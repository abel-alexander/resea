def toc_with_llm(text):
    prompt = f"""
    You are an expert at extracting a structured Table of Contents from complex text.
    
    **Instructions:**
    - Extract the hierarchical Table of Contents from the input text.
    - Preserve numbering (e.g., 1., 1.1, i., ii., A., B.).
    - **Return only the Table of Contents in Markdown format. Do not include any explanations.**
    
    **Example Input:**
    ```
    1. Introduction
    2. Financial Overview
       i. Revenue
       ii. Expenses
    3. Market Analysis
       a. Competitor Landscape
       b. Growth Opportunities
    ```

    **Expected Output in Markdown:**
    ```
    # Table of Contents

    - **1. Introduction**
    - **2. Financial Overview**
      - i. Revenue
      - ii. Expenses
    - **3. Market Analysis**
      - a. Competitor Landscape
      - b. Growth Opportunities
    ```

    **Extract and return only the markdown-formatted Table of Contents from this document:**
    ```
    {text}
    ```
    """
    
    response = llm(prompt, max_length=5000)  # Limit output length to avoid extra text
    return response.strip()  # Ensure no extra whitespace

# Call LLM
llm_score = toc_with_llm(pg)

# Extract only the markdown content if LLM returns extra text
if isinstance(llm_score, dict):  
    llm_score = llm_score.get("text", "").strip()

# Ensure we only show markdown without explanations
if "Table of Contents" in llm_score:
    llm_score = llm_score.split("Table of Contents")[-1].strip()

# Display properly formatted ToC
from IPython.display import display, Markdown
display(Markdown(llm_score))
