import pandas as pd
import plotly.express as px

# Load the data
file_path = "your_excel_file.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path, sheet_name='parsed_logs')

# Convert 'Timestamp' to datetime and set as index
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.set_index('Timestamp', inplace=True)

# Resample data to ensure continuous time series at a desired frequency (e.g., 1 minute)
summary_counts = df[df['Action'] == 'sum:result:summary'].resample('T').size().rename('Summary Count')
qa_counts = df[df['Action'] == 'qa:result'].resample('T').size().rename('QA Count')
overall_counts = df.resample('T').size().rename('Overall Count')

# Combine all counts into a single DataFrame
merged_df = pd.concat([summary_counts, qa_counts, overall_counts], axis=1).fillna(0)

# Reset index for plotting
merged_df.reset_index(inplace=True)

# Plot the time series using Plotly
fig = px.line(
    merged_df, 
    x='Timestamp', 
    y=['Summary Count', 'QA Count', 'Overall Count'],
    title='Time Series of Actions with Resampling',
    labels={'value': 'Action Count', 'Timestamp': 'Time'},
    line_shape='linear',
    markers=True
)

# Show the plot
fig.show()
