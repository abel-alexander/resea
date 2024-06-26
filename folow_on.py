import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from io import BytesIO
import re

def main():
    st.title('Dataframe Comparator')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("First Dataset")
        uploaded_file1 = st.file_uploader("Upload a CSV file", key="file1")

    with col2:
        st.subheader("Second Dataset")
        uploaded_file2 = st.file_uploader("Upload a CSV file", key="file2")

    df1, df2 = None, None

    if uploaded_file1:
        df1 = load_csv(uploaded_file1)
        if df1 is not None:
            df1 = clean_dataframe(df1)
        else:
            st.error("Error reading the first file. Please check the file format and encoding.")

    if uploaded_file2:
        df2 = load_csv(uploaded_file2)
        if df2 is not None:
            df2 = clean_dataframe(df2)
        else:
            st.error("Error reading the second file. Please check the file format and encoding.")

    if df1 is not None and df2 is not None:
        col1_name = st.selectbox('Select the column to compare from the first dataset:', df1.columns)
        col2_name = st.selectbox('Select the column to compare from the second dataset:', df2.columns)

        if st.button('Compare'):
            results = compare_columns(df1, df2, col1_name, col2_name)
            st.write(results)
            st.download_button(
                label="Download Results as Excel",
                data=convert_df_to_excel(results),
                file_name='comparison_results.xlsx',
                mime='application/vnd.ms-excel'
            )

def load_csv(uploaded_file):
    try:
        return pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return pd.read_csv(uploaded_file, encoding='latin1')
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\bcorporation\b', 'corp', text)
    text = re.sub(r'\blimited\b', 'ltd', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    text = text.strip()
    return text

def clean_dataframe(df):
    df = df.applymap(lambda s: clean_text(s) if type(s) is str else s)
    return df

def compare_columns(df1, df2, col1, col2):
    results = pd.DataFrame(columns=[col1, col2, 'Flag'])
    result_list = []

    for name1 in df1[col1]:
        name1_words = name1.split()
        best_match = None
        best_flag = 0

        for name2 in df2[col2]:
            name2_words = name2.split()
            if name1 == name2:
                flag = 10
            elif name1_words[:3] == name2_words[:3]:
                flag = 3
            elif name1_words[:2] == name2_words[:2]:
                flag = 2
            elif name1_words[:1] == name2_words[:1]:
                flag = 1
            else:
                flag = 0

            if flag > best_flag:
                best_flag = flag
                best_match = name2

        result_list.append({
            col1: name1,
            col2: best_match,
            'Flag': best_flag
        })

    results = pd.concat([results, pd.DataFrame(result_list)], ignore_index=True)
    return results

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.save()
    processed_data = output.getvalue()
    return processed_data

if __name__ == "__main__":
    main()
