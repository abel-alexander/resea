import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from io import StringIO, BytesIO

def main():
    st.title('Dataframe Comparator')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("First Dataset")
        uploaded_file1 = st.file_uploader("Upload a CSV file", key="file1")
        text_data1 = st.text_area("Or paste CSV data here", height=300, key="text1")

    with col2:
        st.subheader("Second Dataset")
        uploaded_file2 = st.file_uploader("Upload a CSV file", key="file2")
        text_data2 = st.text_area("Or paste CSV data here", height=300, key="text2")

    df1, df2 = None, None

    if uploaded_file1 or text_data1:
        df1 = pd.read_csv(StringIO(text_data1)) if text_data1 else pd.read_csv(uploaded_file1)
        df1 = df1.applymap(lambda s: s.lower() if type(s) is str else s)

    if uploaded_file2 or text_data2:
        df2 = pd.read_csv(StringIO(text_data2)) if text_data2 else pd.read_csv(uploaded_file2)
        df2 = df2.applymap(lambda s: s.lower() if type(s) is str else s)

    if df1 is not None and df2 is not None:
        col1_name = st.selectbox('Select the column to compare from the first dataset:', df1.columns)
        col2_name = st.selectbox('Select the column to compare from the second dataset:', df2.columns)
        num_letters = st.number_input('Number of initial letters to match', min_value=1, value=4)
        threshold = st.slider('Fuzzy similarity threshold', min_value=0, max_value=100, value=90)

        if st.button('Compare'):
            results = compare_columns(df1, df2, col1_name, col2_name, num_letters, threshold)
            st.write(results)
            st.download_button(
                label="Download Results as Excel",
                data=convert_df_to_excel(results),
                file_name='comparison_results.xlsx',
                mime='application/vnd.ms-excel'
            )

def compare_columns(df1, df2, col1, col2, num_letters, threshold):
    results = pd.DataFrame(columns=[col1, 'Matched Value from Second Dataset', 'Matching Similarity', 'Matched Letters', 'Suggested Match', 'Suggested Matching Similarity'])

    for name1 in df1[col1]:
        best_match = None
        best_score = 0
        best_letters_matched = ""
        second_best_match = None
        second_best_score = 0
        second_best_letters_matched = ""

        for name2 in df2[col2]:
            score = fuzz.ratio(name1, name2)
            letters_matched = name1[:num_letters] if name1[:num_letters] == name2[:num_letters].replace(" ", "") else ""
            if letters_matched and score >= threshold:
                if score > best_score:
                    best_score, best_match, best_letters_matched = score, name2, letters_matched

            if score > second_best_score:
                second_best_score, second_best_match, second_best_letters_matched = score, name2, letters_matched

        results = results.append({
            col1: name1,
            'Matched Value from Second Dataset': best_match,
            'Matching Similarity': best_score,
            'Matched Letters': best_letters_matched,
            'Suggested Match': second_best_match,
            'Suggested Matching Similarity': second_best_score
        }, ignore_index=True)

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
