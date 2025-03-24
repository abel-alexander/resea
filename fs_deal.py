import json

# === Load glossary from JSON file ===
with open("glossary.json", "r") as f:
    glossary_data = json.load(f)

# === Load full valuation framework from a text file ===
with open("valuation_framework_full.txt", "r") as f:
    valuation_framework_text = f.read()


# === Helper: Expand acronyms in query ===
def expand_query_with_glossary(query):
    words = query.split()
    expanded_words = []

    for word in words:
        match = glossary_data.get(word.upper())
        if match:
            expanded_words.append(f"{word} ({match})")
        else:
            expanded_words.append(word)

    return " ".join(expanded_words)


# === Helper: Determine if the query is valuation-related ===
def is_valuation_query(query):
    valuation_keywords = {
        "valuation", "discounted cash flow", "intrinsic value",
        "terminal value", "multiple", "ebitda", "dcf"
    }

    query_lower = query.lower()
    has_keyword = any(term in query_lower for term in valuation_keywords)

    words = query.split()
    has_acronym = any(word.upper() in glossary_data for word in words)

    return has_acronym, has_keyword


# === Main Function ===
def get_context_from_query(query):
    expanded_query = expand_query_with_glossary(query)
    has_acronym, has_keyword = is_valuation_query(query)

    if has_acronym:
        source = "acronym_detected"
        context = valuation_framework_text
    elif has_keyword:
        source = "valuation_keywords_detected"
        context = valuation_framework_text
    else:
        source = "general_query"
        context = None  # fallback to FAISS or other source

    return {
        "query": expanded_query,
        "context": context,
        "source": source
    }
