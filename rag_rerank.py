import pandas as pd
import plotly.express as px

# Load the data
file_path = "your_excel_file.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path, sheet_name='parsed_logs')

# Convert 'Timestamp' to datetime and set as index
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.set_index('Timestamp', inplace=True)

# Calculate cumulative counts
summary_cumsum = (df['Action'] == 'sum:result:summary').resample('T').sum().cumsum().rename('Summary Count')
qa_cumsum = (df['Action'] == 'qa:result').resample('T').sum().cumsum().rename('QA Count')
overall_cumsum = df.resample('T').size().cumsum().rename('Overall Count')

# Combine cumulative counts into a single DataFrame
merged_df = pd.concat([summary_cumsum, qa_cumsum, overall_cumsum], axis=1).fillna(0)

# Reset index for plotting
merged_df.reset_index(inplace=True)

# Melt the DataFrame for easier plotting
melted_df = merged_df.melt(id_vars='Timestamp', value_vars=['Summary Count', 'QA Count', 'Overall Count'],
                           var_name='Action Type', value_name='Cumulative Count')

# Plot the cumulative bar chart
fig = px.bar(
    melted_df,
    x='Timestamp',
    y='Cumulative Count',
    color='Action Type',
    title='Cumulative Actions as a Bar Chart',
    labels={'Cumulative Count': 'Cumulative Count', 'Timestamp': 'Time'},
    barmode='group'
)

# Show the plot
fig.show()
