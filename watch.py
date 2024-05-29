if chart_type == 'clustered':
            df_sorted = df.sort_values(by=['Bank', 'Valuation Feedback'], ascending=[True, False])
            df_sorted.to_excel(excel_writer, sheet_name=sheet_name, header=True, startrow=1, index=False)

            # Create a clustered column chart
            chart = workbook.add_chart({'type': 'column'})

            banks = df_sorted['Bank'].unique()
            row = 2  # Start from the second row (first row after header)

            for bank in banks:
                bank_data = df_sorted[df_sorted['Bank'] == bank]
                for feedback in ['Yes', 'No']:
                    feedback_data = bank_data[bank_data['Valuation Feedback'] == feedback]
                    if not feedback_data.empty:
                        color = 'navy' if feedback == 'Yes' else 'red'
                        chart.add_series({
                            'name': f"{bank} - {feedback}",
                            'categories': f"='{sheet_name}'!$A${row}:$A${row}",
                            'values': f"='{sheet_name}'!$C${feedback_data.index[0] + 2}:$C${feedback_data.index[0] + 2}",
                            'fill': {'color': color},
                            'data_labels': {'value': True, 'position': 'outside_end'},
                        })
                row += 1

            chart.set_chartarea({'fill': {'none': True}, 'border': {'none': True}})
            chart.set_plotarea({'fill': {'none': True}})
            chart.set_x_axis({
                'name': 'Bank',
                'major_gridlines': {'visible': False},
            })
            chart.set_y_axis({'visible': False, 'major_gridlines': {'visible': False}})
            chart.set_legend({'position': 'bottom'})

            worksheet.insert_chart('E2', chart)
