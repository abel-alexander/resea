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


# Define the path to your Excel files (e.g., using glob to find all Excel files in a directory)
file_paths = glob.glob("path_to_your_excel_files/*.xlsx")

# Compile the data
df_green, df_not_green = compile_data(file_paths)

# Aggregate frequencies
df_green_aggregated = aggregate_frequencies(df_green)
df_not_green_aggregated = aggregate_frequencies(df_not_green)

# Print the results or save them to a new Excel file
print("Aggregated DataFrame with 'Yes' in 'Keep' column:")
print(df_green_aggregated)
print("\nAggregated DataFrame without 'Yes' in 'Keep' column:")
print(df_not_green_aggregated)

# Optionally, save to new Excel files
df_green_aggregated.to_excel("yes_keep_aggregated.xlsx", index=False)
df_not_green_aggregated.to_excel("no_keep_aggregated.xlsx", index=False)
