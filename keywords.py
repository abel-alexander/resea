import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
import glob


def is_cell_green(cell):
    """Check if a cell is filled with green color."""
    if cell.fill.start_color.index == '00000000' and cell.fill.end_color.index == '00000000':
        return False
    green_color = 'FF00FF00'  # Hex code for green color
    return cell.fill.start_color.index == green_color or cell.fill.end_color.index == green_color


def compile_data(file_paths):
    """Compile data from multiple Excel files into two separate DataFrames based on 'Keep' column color."""
    df_green = pd.DataFrame(columns=['Keyword', 'Frequency', 'Keep'])
    df_not_green = pd.DataFrame(columns=['Keyword', 'Frequency', 'Keep'])

    for file_path in file_paths:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        for row in sheet.iter_rows(min_row=2, values_only=False):  # Assuming the first row is header
            keyword = row[0].value
            frequency = row[1].value
            keep = row[2].value
            cell = row[2]

            row_data = {'Keyword': keyword, 'Frequency': frequency, 'Keep': keep}

            if is_cell_green(cell):
                df_green = df_green.append(row_data, ignore_index=True)
            else:
                df_not_green = df_not_green.append(row_data, ignore_index=True)

    return df_green, df_not_green


# Define the path to your Excel files (e.g., using glob to find all Excel files in a directory)
file_paths = glob.glob("path_to_your_excel_files/*.xlsx")

# Compile the data
df_green, df_not_green = compile_data(file_paths)

# Print the results or save them to a new Excel file
print("DataFrame with green 'Keep' cells:")
print(df_green)
print("\nDataFrame without green 'Keep' cells:")
print(df_not_green)

# Optionally, save to new Excel files
df_green.to_excel("green_keep.xlsx", index=False)
df_not_green.to_excel("not_green_keep.xlsx", index=False)
