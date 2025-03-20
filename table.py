def expand_query_with_glossary(query):
    """Check if the query contains an acronym and expand it."""
    words = query.split()
    expanded_words = []

    for word in words:
        glossary_match = retrieve_from_glossary(word)  # Check if word is in glossary
        if glossary_match:
            expanded_words.append(f"{word} ({glossary_match})")
        else:
            expanded_words.append(word)

    return " ".join(expanded_words)


def retrieve_from_faiss(query, top_k=3):
    """Retrieves relevant chunks from FAISS (first glossary, then valuation framework)."""
    expanded_query = expand_query_with_glossary(query)  # Expand query before retrieval
    query_embedding = model.encode([expanded_query])

    # First, check glossary FAISS index
    _, glossary_indices = glossary_index.search(np.array(query_embedding, dtype=np.float32), top_k)
    with open("faiss_glossary_mapping.json", "r") as f:
        stored_glossary = json.load(f)

    glossary_results = [stored_glossary[i] for i in glossary_indices[0] if i < len(stored_glossary)]

    # If glossary has an exact match, return only that
    exact_glossary_match = retrieve_from_glossary(query)
    if exact_glossary_match:
        return [exact_glossary_match]  # Stop here if it's an acronym query

    # Otherwise, check valuation framework
    _, indices = val_index.search(np.array(query_embedding, dtype=np.float32), top_k)
    with open("faiss_valuation_mapping.json", "r") as f:
        stored_definitions = json.load(f)

    valuation_results = [stored_definitions[i] for i in indices[0] if i < len(stored_definitions)]

    return glossary_results + valuation_results
