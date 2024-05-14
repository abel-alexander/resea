import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import faiss
import evaluate


# Placeholder function to get model name
def get_name_util(name):
    # Replace this with the actual implementation of get_name_util
    return name


# Function to clear text inputs
def clear_text_inputs():
    st.session_state['model1_text'] = ''
    st.session_state['model2_text'] = ''
    st.session_state['model3_text'] = ''
    st.session_state['model1_token_limit'] = 100
    st.session_state['model2_token_limit'] = 100
    st.session_state['model3_token_limit'] = 100
    st.session_state['model1_temperature'] = 0.7
    st.session_state['model2_temperature'] = 0.7
    st.session_state['model3_temperature'] = 0.7
    st.session_state['model1_prompt'] = ''
    st.session_state['model2_prompt'] = ''
    st.session_state['model3_prompt'] = ''
    st.session_state['common_task'] = ''
    st.session_state['reference_text'] = ''
    st.session_state['model1_rouge1'] = 0.0
    st.session_state['model2_rouge1'] = 0.0
    st.session_state['model3_rouge1'] = 0.0
    st.session_state['model1_rouge2'] = 0.0
    st.session_state['model2_rouge2'] = 0.0
    st.session_state['model3_rouge2'] = 0.0
    st.session_state['model1_rougel'] = 0.0
    st.session_state['model2_rougel'] = 0.0
    st.session_state['model3_rougel'] = 0.0


# Initialize session state for text areas and parameters if not already present
if 'model1_text' not in st.session_state:
    st.session_state['model1_text'] = ''
if 'model2_text' not in st.session_state:
    st.session_state['model2_text'] = ''
if 'model3_text' not in st.session_state:
    st.session_state['model3_text'] = ''
if 'model1_token_limit' not in st.session_state:
    st.session_state['model1_token_limit'] = 100
if 'model2_token_limit' not in st.session_state:
    st.session_state['model2_token_limit'] = 100
if 'model3_token_limit' not in st.session_state:
    st.session_state['model3_token_limit'] = 100
if 'model1_temperature' not in st.session_state:
    st.session_state['model1_temperature'] = 0.7
if 'model2_temperature' not in st.session_state:
    st.session_state['model2_temperature'] = 0.7
if 'model3_temperature' not in st.session_state:
    st.session_state['model3_temperature'] = 0.7
if 'model1_prompt' not in st.session_state:
    st.session_state['model1_prompt'] = ''
if 'model2_prompt' not in st.session_state:
    st.session_state['model2_prompt'] = ''
if 'model3_prompt' not in st.session_state:
    st.session_state['model3_prompt'] = ''
if 'common_task' not in st.session_state:
    st.session_state['common_task'] = ''
if 'reference_text' not in st.session_state:
    st.session_state['reference_text'] = ''
if 'model1_rouge1' not in st.session_state:
    st.session_state['model1_rouge1'] = 0.0
if 'model2_rouge1' not in st.session_state:
    st.session_state['model2_rouge1'] = 0.0
if 'model3_rouge1' not in st.session_state:
    st.session_state['model3_rouge1'] = 0.0
if 'model1_rouge2' not in st.session_state:
    st.session_state['model1_rouge2'] = 0.0
if 'model2_rouge2' not in st.session_state:
    st.session_state['model2_rouge2'] = 0.0
if 'model3_rouge2' not in st.session_state:
    st.session_state['model3_rouge2'] = 0.0
if 'model1_rougel' not in st.session_state:
    st.session_state['model1_rougel'] = 0.0
if 'model2_rougel' not in st.session_state:
    st.session_state['model2_rougel'] = 0.0
if 'model3_rougel' not in st.session_state:
    st.session_state['model3_rougel'] = 0.0


# Function to calculate ROUGE scores
def calculate_rouge_scores():
    scorer = evaluate.load('rouge')
    for i in range(3):
        generated_text = st.session_state[f'model{i + 1}_text']
        reference_text = st.session_state['reference_text']
        if generated_text and reference_text:
            scores = scorer.compute(predictions=[generated_text], references=[reference_text])
            st.session_state[f'model{i + 1}_rouge1'] = scores['rouge1'].mid.fmeasure
            st.session_state[f'model{i + 1}_rouge2'] = scores['rouge2'].mid.fmeasure
            st.session_state[f'model{i + 1}_rougel'] = scores['rougeL'].mid.fmeasure


# Function to save details to an Excel file
def save_to_excel():
    data = {
        'Model': [f'Model {i + 1}' for i in range(3)],
        'Selected Model': [st.session_state[f'model_select_{i + 1}'] for i in range(3)],
        'Prompt': [st.session_state[f'model{i + 1}_prompt'] for i in range(3)],
        'Generated Text': [st.session_state[f'model{i + 1}_text'] for i in range(3)],
        'Token Limit': [st.session_state[f'model{i + 1}_token_limit'] for i in range(3)],
        'Temperature': [st.session_state[f'model{i + 1}_temperature'] for i in range(3)],
        'ROUGE-1': [st.session_state[f'model{i + 1}_rouge1'] for i in range(3)],
        'ROUGE-2': [st.session_state[f'model{i + 1}_rouge2'] for i in range(3)],
        'ROUGE-L': [st.session_state[f'model{i + 1}_rougel'] for i in range(3)],
        'Common Task/Question': [st.session_state['common_task']] * 3,
        'Reference Text': [st.session_state['reference_text']] * 3
    }
    df = pd.DataFrame(data)
    df.to_excel('run_details.xlsx', index=False)
    st.success("Details saved to 'run_details.xlsx'")


# Layout
st.title('Model Selection and Text Generation')

# Common file uploader
uploaded_file = st.file_uploader("Choose a file")

# Common task/chat space
st.text_area('Common Task/Question Space', st.session_state['common_task'], key='common_task')

# Reference text space
st.text_area('Reference Text', st.session_state['reference_text'], key='reference_text')

# Columns for model selection, prompts, and generated text
cols = st.columns(3)

models = ['llama2-7b-chat', 'Model B', 'Model C']

for i, col in enumerate(cols):
    with col:
        model_name = st.selectbox('Select model {}'.format(i + 1), models, key='model_select_{}'.format(i + 1))
        prompt = st.text_area('Enter prompt {}'.format(i + 1), st.session_state['model{}_prompt'.format(i + 1)],
                              key='model{}_prompt'.format(i + 1))
        generated_text = st.text_area('Generated Text {}'.format(i + 1), st.session_state['model{}_text'.format(i + 1)],
                                      key='model{}_text'.format(i + 1))
        token_limit = st.number_input('Token Limit {}'.format(i + 1), min_value=1, max_value=1000,
                                      value=st.session_state['model{}_token_limit'.format(i + 1)],
                                      key='model{}_token_limit'.format(i + 1))
        temperature = st.slider('Temperature {}'.format(i + 1), min_value=0.0, max_value=1.0,
                                value=st.session_state['model{}_temperature'.format(i + 1)],
                                key='model{}_temperature'.format(i + 1))

        # Handle model loading when llama2-7b-chat is selected
        if model_name == 'llama2-7b-chat':
            model_name_util = get_name_util(name='llama2-7b-chat')
            model = AutoModelForCausalLM.from_pretrained(model_name_util)
            tokenizer = AutoTokenizer.from_pretrained(model_name_util)
            # Assuming the embedding process and FAISS indexing here
            embedding = model.get_input_embeddings()
            index = faiss.IndexFlatL2(embedding.weight.shape[1])
            index.add(embedding.weight.cpu().detach().numpy())
            # Store the embedding and use it to generate output
            inputs = tokenizer(prompt, return_tensors='pt')
            outputs = model.generate(inputs.input_ids, max_length=token_limit, temperature=temperature)
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            st.session_state['model{}_text'.format(i + 1)] = generated_text

        # Calculate ROUGE scores after generating text
        calculate_rouge_scores()

        # Display ROUGE scores
        st.markdown('ROUGE-1 {}: {:.4f}'.format(i + 1, st.session_state['model{}_rouge1'.format(i + 1)]))
        st.markdown('ROUGE-2 {}: {:.4f}'.format(i + 1, st.session_state['model{}_rouge2'.format(i + 1)]))
        st.markdown('ROUGE-L {}: {:.4f}'.format(i + 1, st.session_state['model{}_rougel'.format(i + 1)]))

# Common clear button
if st.button('Clear All'):
    clear_text_inputs()

# Save details to Excel button
if st.button('Save Details to Excel'):
    save_to_excel()
