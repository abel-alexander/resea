import re
from IPython.display import display, Markdown

# Run LLM with stricter settings
response = chain.run(extracted_toc_ocr)

# Step 1: Extract only ToC (remove hallucinated explanations)
match = re.search(r"<TOC_START>(.*?)<TOC_END>", response, re.DOTALL)
if match:
    cleaned_toc = match.group(1).strip()
else:
    cleaned_toc = response.strip()  # Fallback in case delimiters are missing

# Step 2: Remove unwanted code blocks or hallucinated output
cleaned_toc = re.sub(r"```.*?```", "", cleaned_toc, flags=re.DOTALL)  # Remove any hallucinated code
cleaned_toc = re.sub(r"\b(function|import|print|def|return|self|if|else|while|for|class)\b.*", "", cleaned_toc)  # Remove hallucinated Python functions

# Step 3: Remove excessive newlines
cleaned_toc = re.sub(r"\n{3,}", "\n\n", cleaned_toc).strip()

# Display clean Markdown output
display(Markdown(cleaned_toc))
