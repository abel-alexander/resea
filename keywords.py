import pandas as pd
import glob


def compile_data(file_paths):
    """Compile data from multiple Excel files into two separate DataFrames based on 'Keep' column value."""
    df_green_list = []
    df_not_green_list = []

    for file_path in file_paths:
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            row_data = {'Keyword': row['Keyword'], 'Frequency': row['Frequency'], 'Keep': row['Keep']}

            if row['Keep'] == 'Yes':
                df_green_list.append(row_data)
            else:
                df_not_green_list.append(row_data)

    df_green = pd.DataFrame(df_green_list)
    df_not_green = pd.DataFrame(df_not_green_list)

    return df_green, df_not_green


def aggregate_frequencies(df):
    """Aggregate frequency values for rows with the same keyword."""
    return df.groupby('Keyword', as_index=False).agg({'Frequency': 'sum'})


def remove_common_keywords(df1, df2):
    """Remove rows from df2 that have keywords present in df1."""
    common_keywords = set(df1['Keyword'])
    return df2[~df2['Keyword'].isin(common_keywords)]


# Define the path to your Excel files (e.g., using glob to find all Excel files in a directory)
file_paths = glob.glob("path_to_your_excel_files/*.xlsx")

# Compile the data
df_green, df_not_green = compile_data(file_paths)

# Aggregate frequencies
df_green_aggregated = aggregate_frequencies(df_green)
df_not_green_aggregated = aggregate_frequencies(df_not_green)

# Remove common keywords from no_keep_aggregated
df_not_green_aggregated = remove_common_keywords(df_green_aggregated, df_not_green_aggregated)

# Print the results or save them to a new Excel file
print("Aggregated DataFrame with 'Yes' in 'Keep' column:")
print(df_green_aggregated)
print("\nAggregated DataFrame without 'Yes' in 'Keep' column (after removing common keywords):")
print(df_not_green_aggregated)

# Optionally, save to new Excel files
df_green_aggregated.to_excel("yes_keep_aggregated.xlsx", index=False)
df_not_green_aggregated.to_excel("no_keep_aggregated.xlsx", index=False)
