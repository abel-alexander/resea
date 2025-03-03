from transformers import pipeline

llm = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1")

def evaluate_with_llm(reference, generated):
    prompt = f"""
    You are an expert evaluator. Compare the generated summary with the reference summary.
    
    Reference Summary:
    {reference}
    
    Generated Summary:
    {generated}

    Provide a score between 0 and 10 based on correctness, coherence, and relevance. Explain briefly.
    """
    response = llm(prompt, max_length=100)
    return response[0]['generated_text']  # Extract score

llm_score = evaluate_with_llm(ref_text, result)
print("LLM Score:", llm_score)
