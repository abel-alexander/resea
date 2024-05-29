if chart_type == 'clustered':
            df_sorted = df.sort_values(by=['Bank', 'Valuation Feedback'], ascending=[True, False])
            df_sorted.to_excel(excel_writer, sheet_name=sheet_name, header=True, startrow=1, index=False)

            # Create a clustered column chart
            chart = workbook.add_chart({'type': 'column'})

            for feedback in ['Yes', 'No']:
                feedback_data = df_sorted[df_sorted['Valuation Feedback'] == feedback]
                color = 'navy' if feedback == 'Yes' else 'red'
                chart.add_series({
                    'name': feedback,
                    'categories': f"='{sheet_name}'!$A$2:$A${len(df_sorted) + 1}",
                    'values': f"='{sheet_name}'!$C$2:$C${len(feedback_data) + 2}",
                    'fill': {'color': color},
                    'data_labels': {'value': True, 'position': 'outside_end'},
                })

            chart.set_chartarea({'fill': {'none': True}, 'border': {'none': True}})
            chart.set_plotarea({'fill': {'none': True}})
            chart.set_x_axis({
                'name': 'Bank',
                'categories': f"='{sheet_name}'!$A$2:$A${len(df_sorted) + 1}",
                'major_gridlines': {'visible': False},
            })
            chart.set_y_axis({'visible': False, 'major_gridlines': {'visible': False}})
            chart.set_legend({'position': 'bottom'})

            worksheet.insert_chart('E2', chart)
