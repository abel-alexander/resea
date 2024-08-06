import streamlit as st
import pandas as pd
from io import BytesIO
import re

def main():
    st.title('Dataframe Comparator')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("First Dataset (Factset)")
        uploaded_file1 = st.file_uploader("Upload an Excel file", type=["xlsx"], key="file1")

    with col2:
        st.subheader("Second Dataset (Dealogic)")
        uploaded_file2 = st.file_uploader("Upload an Excel file", type=["xlsx"], key="file2")

    df1, df2 = None, None

    if uploaded_file1:
        df1 = load_excel(uploaded_file1)
        if df1 is not None:
            df1 = clean_dataframe(df1)
        else:
            st.error("Error reading the first file. Please check the file format and encoding.")

    if uploaded_file2:
        df2 = load_excel(uploaded_file2)
        if df2 is not None:
            df2 = clean_dataframe(df2)
        else:
            st.error("Error reading the second file. Please check the file format and encoding.")

    if df1 is not None and df2 is not None:
        if 'fs-ticker' in df1.columns and 'ticker' in df2.columns and 'currency' in df2.columns:
            df1, df2 = compare_and_flag_tickers(df1, df2)

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

def load_excel(uploaded_file):
    try:
        return pd.read_excel(uploaded_file)
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

def compare_and_flag_tickers(df1, df2):
    df1['ticker'] = df1['fs-ticker'].apply(lambda x: x.split('-')[0] if '-' in x else x)
    df1['matched_company'] = None
    df1['match_flag'] = None

    for idx1, row1 in df1.iterrows():
        ticker1 = row1['ticker']
        for idx2, row2 in df2.iterrows():
            if ticker1 == row2['ticker']:
                df1.at[idx1, 'matched_company'] = row2['CompanyName']
                df1.at[idx1, 'match_flag'] = 'Ticker Match'
                break

    return df1, df2

def compare_columns(df1, df2, col1, col2):
    results = pd.DataFrame(columns=[col1, 'Flag 10', 'Flag 3', 'Flag 2', 'Flag 1', 'Flag 0'])
    result_list = []

    for name1 in df1[col1]:
        name1_words = name1.split()
        matches = {'Flag 10': None, 'Flag 3': None, 'Flag 2': None, 'Flag 1': None, 'Flag 0': None}

        for name2 in df2[col2]:
            name2_words = name2.split()
            if name1 == name2:
                matches['Flag 10'] = name2
            elif name1_words[:3] == name2_words[:3] and matches['Flag 10'] is None:
                matches['Flag 3'] = name2
            elif name1_words[:2] == name2_words[:2] and matches['Flag 10'] is None and matches['Flag 3'] is None:
                matches['Flag 2'] = name2
            elif name1_words[:1] == name2_words[:1] and matches['Flag 10'] is None and matches['Flag 3'] is None and matches['Flag 2'] is None:
                matches['Flag 1'] = name2
            elif matches['Flag 10'] is None and matches['Flag 3'] is None and matches['Flag 2'] is None and matches['Flag 1'] is None:
                matches['Flag 0'] = name2

        result_list.append({
            col1: name1,
            'Flag 10': matches['Flag 10'],
            'Flag 3': matches['Flag 3'],
            'Flag 2': matches['Flag 2'],
            'Flag 1': matches['Flag 1'],
            'Flag 0': matches['Flag 0']
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
