Perfect — thanks for the clarification. Let's walk through it cleanly:

---

### ✅ Your Current Function — Summary

It:
- Extracts ToC by matching "Table of Contents"
- Falls back to matching `1.` if ToC isn't found
- Merges lines like `a)\nTitle`
- Handles:
  - `1.`, `i.`, `a)`, `b.` as hierarchy levels
- Strips prefixes and maps page numbers

---

### ✅ What's Missing

From your current code:
- It **doesn’t support bullets like `-`, `•`, or `–`**
- Fallback match for `1.` fails if newline follows `1.` (you use `\s+`, which doesn’t catch newlines)
- No normalization of bullet characters

---

### ✅ Proposed Fix — Built On Your Version

Here’s the final **drop-in** that:
1. **Fixes the fallback to handle `1.\nTitle`**
2. **Handles `a)`, `b.`, `-`, `•`, `–` as level 2**
3. **Normalizes bullets**
4. **Does not alter working logic you already had**

---

### ✅ Final Updated Function (built strictly on your version)

```python
import fitz  # PyMuPDF
import re

def extract_toc_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text("text")

    # Try extracting text after "Table of Contents"
    match = re.search(r"Table of Contents(.*)", first_page_text, re.DOTALL)
    if match:
        toc_text = match.group(1).strip()
    else:
        # Fallback: Start from the first numbered section like "1." even with newline after
        match = re.search(r"\b1\.\s*(.*)", first_page_text, re.DOTALL)
        if not match:
            return []  # No ToC fallback found
        toc_text = "1. " + match.group(1).strip()

    # Normalize bullets/dashes
    toc_text = toc_text.replace("•", "-").replace("–", "-")

    # Merge broken lines like "a)\nTitle" or "-\nTitle"
    toc_text = re.sub(r"(\d+\.|[ivxlc]+\.|[a-zA-Z][\.\)]|-)\n", r"\1 ", toc_text, flags=re.IGNORECASE)

    # Split and process
    toc_list = []
    for line in toc_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Detect hierarchy level
        if re.match(r"^\d+\.", line):  # e.g., "1. Title"
            level = 1
        elif re.match(r"^([ivxlc]+\.|[a-zA-Z][\.\)]|- )", line, re.IGNORECASE):  # e.g., "a)", "b.", "- Title"
            level = 2
        else:
            continue

        # Remove prefix
        section_name = re.sub(r"^(\d+\.\s*|[ivxlc]+\.\s*|[a-zA-Z][\.\)]\s*|- )", "", line, flags=re.IGNORECASE).strip()
        toc_list.append([level, section_name, None])

    # Extract page links
    first_page_links = doc[0].get_links()
    page_numbers = [int(link["page"]) + 1 for link in first_page_links if "page" in link]

    # Assign page numbers
    page_index = 0
    for i in range(len(toc_list)):
        if toc_list[i][0] == 1:
            if page_index < len(page_numbers):
                toc_list[i][2] = page_numbers[page_index]
                page_index += 1
            if i + 1 < len(toc_list) and toc_list[i + 1][0] == 2:
                toc_list[i + 1][2] = toc_list[i][2]
        elif toc_list[i][0] == 2 and toc_list[i][2] is None:
            if page_index < len(page_numbers):
                toc_list[i][2] = page_numbers[page_index]
                page_index += 1

    return toc_list
```

---

Let me know if you want:
- Grouping under each section
- To detect titles even without bullets or indexes (pure indentation or case-based)
