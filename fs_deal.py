import streamlit as st
import pandas as pd
from io import BytesIO
import re

def main():
    st.title('Dataframe Comparator')

    # Commenting out the upload option
    # col1, col2 = st.columns(2)

    # with col1:
    #     st.subheader("First Dataset (Factset)")
    #     uploaded_file1 = st.file_uploader("Upload an Excel file", type=["xlsx"], key="file1")

    # with col2:
    #     st.subheader("Second Dataset (Dealogic)")
    #     uploaded_file2 = st.file_uploader("Upload an Excel file", type=["xlsx"], key="file2")

    df1, df2 = None, None

    # Replace with directory path
    file_path1 = 'path/to/factset.xlsx'  # Update this path
    file_path2 = 'path/to/dealogic.xlsx'  # Update this path

    # Load the Excel files directly from the specified path
    df1 = load_excel(file_path1)
    if df1 is not None:
        df1 = clean_dataframe(df1)
    else:
        st.error("Error reading the first file. Please check the file format and encoding.")

    df2 = load_excel(file_path2)
    if df2 is not None:
        df2 = clean_dataframe(df2)
    else:
        st.error("Error reading the second file. Please check the file format and encoding.")

    if df1 is not None and df2 is not None:
        if 'FsTicker' in df1.columns and 'ticker_dealogic' in df2.columns and 'currency_dealogic' in df2.columns:
            changed_names = update_combined_ticker_and_names(df1, df2)
            st.subheader("Names Changed Due to Ticker Logic")
            st.write(changed_names)

        # Automatically select the column names for comparison
        col1_name = 'CompanyName'
        col2_name = 'New_name'

        if st.button('Compare'):
            results = compare_columns(df1, df2, col1_name, col2_name)
            st.write(results)
            st.download_button(
                label="Download Results as Excel",
                data=convert_df_to_excel(results),
                file_name='comparison_results.xlsx',
                mime='application/vnd.ms-excel'
            )

def load_excel(file_path):
    try:
        return pd.read_excel(file_path)
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

def update_combined_ticker_and_names(factset_df, dealogic_df):
    dealogic_df['combined_ticker'] = dealogic_df.apply(
        lambda row: f"{row['ticker_dealogic']}-{row['currency_dealogic'][:2].upper()}" if re.match(r'^\d+$', str(row['ticker_dealogic'])) else '', axis=1)
    dealogic_df['New_name'] = dealogic_df['company_dealogic']

    changed_names = []

    for idx, row in dealogic_df.iterrows():
        if row['combined_ticker']:
            combined_ticker = row['combined_ticker']
            fs_ticker_list = factset_df['FsTicker'].tolist()
            print(f"Combined Ticker: {combined_ticker}")
            print(f"FsTicker List: {fs_ticker_list}")
            match = factset_df[factset_df['FsTicker'] == combined_ticker]
            if not match.empty:
                old_name = row['New_name']
                new_name = match['CompanyName'].values[0]
                dealogic_df.at[idx, 'New_name'] = new_name
                changed_names.append({
                    'Combined Ticker': combined_ticker,
                    'Old Name': old_name,
                    'New Name': new_name
                })

    return pd.DataFrame(changed_names)

def compare_columns(df1, df2, col1, col2):
    results = pd.DataFrame(columns=[col1, 'Flag 10', 'Flag 3', 'Flag 2', 'Flag 1', 'Flag 0'])
    result_list = []

    for name1 in df1[col1]:
        matches = {'Flag 10': None, 'Flag 3': None, 'Flag 2': None, 'Flag 1': None, 'Flag 0': None}

        for name2 in df2[col2]:
            if name1 == name2:
                matches['Flag 10'] = name2
            elif name1[:3] == name2[:3] and matches['Flag 10'] is None:
                matches['Flag 3'] = name2
            elif name1[:2] == name2[:2] and matches['Flag 10'] is None and matches['Flag 3'] is None:
                matches['Flag 2'] = name2
            elif name1[:1] == name2[:1] and matches['Flag 10'] is None and matches['Flag 3'] is None and matches['Flag 2'] is None:
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
