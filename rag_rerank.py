import pandas as pd
import plotly.express as px

# Load the data
file_path = "your_excel_file.xlsx"  # Update this with your file path
df = pd.read_excel(file_path, sheet_name='parsed_logs')  # Adjust the sheet name if needed

# Convert 'Timestamp' to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Filter data for 'summary', 'qa', and overall usage
df_summary = df[df['Action'] == 'sum:result:summary']
df_qa = df[df['Action'] == 'qa:result']

# Group counts by timestamp
summary_counts = df_summary.groupby('Timestamp').size().reset_index(name='Count')
qa_counts = df_qa.groupby('Timestamp').size().reset_index(name='Count')
overall_counts = df.groupby('Timestamp').size().reset_index(name='Count')

# Plot all three time series
fig = px.line(summary_counts, x='Timestamp', y='Count', title='Time Series of Actions', 
              labels={'Count': 'Action Count', 'Timestamp': 'Time'}, line_shape='linear', 
              markers=True, color_discrete_sequence=['blue'], 
              template='plotly')

fig.add_scatter(x=qa_counts['Timestamp'], y=qa_counts['Count'], mode='lines+markers',
                name='QA Actions', line=dict(color='red'))
fig.add_scatter(x=overall_counts['Timestamp'], y=overall_counts['Count'], mode='lines+markers',
                name='Overall Usage', line=dict(color='green'))

# Show plot
fig.show()
