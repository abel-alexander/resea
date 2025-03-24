# --- Setup: Load glossary and guideline (if not already done globally) ---
import json
with open("glossary.json", "r") as f:
    glossary_data = json.load(f)

with open("valuation_framework_full.txt", "r") as f:
    guideline_text = f.read()


# --- Step 1: Expand acronyms in the question ---
def expand_query_with_glossary(query):
    words = query.split()
    expanded = []
    changed = False
    for word in words:
        upper = word.upper()
        if upper in glossary_data:
            expanded.append(f"{word} ({glossary_data[upper]})")
            changed = True
        else:
            expanded.append(word)
    return " ".join(expanded), changed


# --- Step 2: Determine if it's valuation-related ---
def is_valuation_query(query):
    valuation_keywords = {"valuation", "dcf", "ebitda", "discounted cash flow", "terminal value", "multiple"}
    return any(kw in query.lower() for kw in valuation_keywords)


# --- Apply logic ---
expanded_question, was_expanded = expand_query_with_glossary(question)
is_val_question = was_expanded or is_valuation_query(question)


if is_val_question:
    prompt = get_qa_prompt(expanded_question, context_text, guideline_text)
else:
    prompt = get_qa_prompt(expanded_question, context_text)
