import pandas as pd
from datetime import datetime

# Step 1: Load and Process Data
# Replace this with your actual data loading step
data = {'Timestamp': ['01/12/24', '30/11/24', '01/12/24', 'InvalidDate'],
        'User': ['John Doe, john@example.com', 'Jane Doe, jane@example.com', 'Jake Doe, jake@example.com', None],
        'Action': ['qa', 'sum', 'qa', None]}
df = pd.DataFrame(data)

# Convert 'Timestamp' to datetime and drop invalid rows
df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%y', errors='coerce')
df = df.dropna(subset=['Timestamp'])

# Normalize 'Timestamp' to midnight to create a 'Date' column (datetime64[ns])
df['Date'] = df['Timestamp'].dt.normalize()

# Step 2: Get today's date as datetime64[ns]
today = pd.Timestamp(datetime.now().date())

# Debug: Check `today` type and sample data
print(f"Today's Date: {today} (type: {type(today)})")
print("\nSample DataFrame after processing:")
print(df.head())

# Step 3: Stats till Date (Aggregated)
stats_till_date = df.groupby('Action').agg(
    Total_Requests=('Action', 'count'),
    Unique_Users=('User', lambda x: len(x.dropna().unique()))
).reset_index()

# Step 4: Stats for Today
df_today = df[df['Date'] == today]  # Filter for today's date
stats_today = df_today.groupby('Action').agg(
    Requests=('Action', 'count'),
    Unique_Users=('User', lambda x: len(x.dropna().unique()))
).reset_index()

# Step 5: Grouped by Dates (Daily Stats)
daily_stats = df.groupby('Date').agg(
    Total_Requests=('Action', 'count'),
    Unique_Users=('User', lambda x: len(x.dropna().unique()))
).reset_index()

# Output the three DataFrames
print("\nStats till Date:")
print(stats_till_date)

print("\nStats for Today:")
print(stats_today)

print("\nDaily Stats (Grouped by Date):")
print(daily_stats)
