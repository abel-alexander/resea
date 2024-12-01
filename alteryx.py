import pandas as pd
from datetime import datetime

# Read input data from Alteryx
df = Alteryx.read("#1")  # "#1" corresponds to the first input anchor in Alteryx

# Ensure the input data contains the expected columns: "Timestamp", "User", and "Action"
df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # Convert the Timestamp column to datetime
df['Date'] = df['Timestamp'].dt.date  # Extract the date for grouping

# Extract today's date
today = datetime.now().date()

# Filter data for today's date
df_today = df[df['Date'] == today]

# Split "User" into "Name" and "Email"
# Assumes User format: "Name, email@example.com"
df_today[['Name', 'Email']] = df_today['User'].str.extract(r'([\w\s]+),\s*([\w\.-]+@[\w\.-]+)')

# Calculate unique QA and SUM counts for today
action_counts_today = df_today.groupby('Action').size().to_dict()

# Get unique users with name and email
unique_users_today = df_today[['Name', 'Email']].drop_duplicates()

# Prepare the unique users as a list of dictionaries for the summary
unique_users_list = unique_users_today.to_dict('records')

# Create the summary DataFrame
summary_data = {
    "Date": [today],
    "QA Count": [action_counts_today.get('qa', 0)],
    "SUM Count": [action_counts_today.get('sum', 0)],
    "Unique Users Count": [len(unique_users_today)],
    "Unique Users Details": [unique_users_list],  # Add unique users as a consolidated field
}

summary_df = pd.DataFrame(summary_data)

# Output the summary DataFrame back to Alteryx
Alteryx.write(summary_df, 1)  # Output the summary with unique user details
