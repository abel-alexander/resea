from rouge_score import rouge_scorer  # Make sure to install rouge_score library if not already

# Define a function to calculate ROUGE score
def calculate_rouge(output, reference):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, output)
    return scores

# Existing code
files = ["file1.pdf", "file2.pdf", ...]  # your files
for file in files:
    st.session_state.pdf_file_name = file
    file_name = f'/path/to/your/files/{file}'  # Update this path as needed

    st.subheader(file)
    q = qa.get_q(i)
    while q != "not found":
        start_time = time.process_time()
        with col_llama:
            rs_llama = mistral.qa2(file_name, q)
            end_time = time.process_time()
            inference_time_llama = end_time - start_time
            st.text(rs_llama)
            st.markdown(rs_llama)

        with col_llama2:
            start_time = time.process_time()
            rs_llama2 = mistral.test_qa(file_name, q)
            end_time = time.process_time()
            inference_time_llama2 = end_time - start_time
            st.text(rs_llama2)
            st.markdown(rs_llama2)

        # Display inference times
        st.write(f"Inference Time (Col Llama): {inference_time_llama} seconds")
        st.write(f"Inference Time (Col Llama2): {inference_time_llama2} seconds")

        # Calculate ROUGE scores between outputs of two columns
        rouge_scores = calculate_rouge(rs_llama, rs_llama2)
        st.write("ROUGE Scores:")
        st.write(f"ROUGE-1: {rouge_scores['rouge1'].fmeasure}")
        st.write(f"ROUGE-2: {rouge_scores['rouge2'].fmeasure}")
        st.write(f"ROUGE-L: {rouge_scores['rougeL'].fmeasure}")

        # Proceed to the next question
        i += 1
        q = qa.get_q(i)
