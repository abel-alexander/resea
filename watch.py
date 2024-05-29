import pandas as pd
import xlsxwriter

def write_dfs_with_charts_to_excel(file_path, dfs_sheet_names_charts_titles_colors):
    excel_writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    workbook = excel_writer.book

    for df, sheet_name, chart_type, chart_title, _ in dfs_sheet_names_charts_titles_colors:
        df.to_excel(excel_writer, sheet_name=sheet_name, startrow=1, index=False)
        worksheet = excel_writer.sheets[sheet_name]

       if chart_type == 'clustered':
            df_sorted = df.sort_values(by=['Bank', 'Valuation Feedback'], ascending=[True, False])
            df_sorted.to_excel(excel_writer, sheet_name=sheet_name, header=True, startrow=1, index=False)

            # Create a clustered column chart
            chart = workbook.add_chart({'type': 'column'})

            banks = df_sorted['Bank'].unique()
            for bank in banks:
                for feedback in ['Yes', 'No']:
                    feedback_data = df_sorted[(df_sorted['Bank'] == bank) & (df_sorted['Valuation Feedback'] == feedback)]
                    if not feedback_data.empty:
                        color = 'navy' if feedback == 'Yes' else 'red'
                        chart.add_series({
                            'name': f"{bank} - {feedback}",
                            'categories': f"='{sheet_name}'!$A$2:$A${len(df_sorted) + 1}",
                            'values': f"='{sheet_name}'!$C${feedback_data.index[0] + 2}:$C${feedback_data.index[0] + 2}",
                            'fill': {'color': color},
                            'data_labels': {'value': True, 'position': 'outside_end'},
                        })

            chart.set_chartarea({'fill': {'none': True}, 'border': {'none': True}})
            chart.set_plotarea({'fill': {'none': True}})
            chart.set_x_axis({'major_gridlines': {'visible': False}})
            chart.set_y_axis({'visible': False, 'major_gridlines': {'visible': False}})
            chart.set_legend({'none': True})

            worksheet.insert_chart('E2', chart)

    excel_writer.save()

# Example usage:
dfs_sheet_names_charts_titles_colors = [
    (df, 'Sheet1', 'stacked', 'Valuation Feedback', None)
]

write_dfs_with_charts_to_excel('output.xlsx', dfs_sheet_names_charts_titles_colors)
