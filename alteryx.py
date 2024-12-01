import pandas as pd
from datetime import datetime

# Example data
data = {'Timestamp': ['01/12/24 08:30:00', '30/11/24 14:45:00', '01/12/24 18:20:00', 'InvalidDate'],
        'User': ['John Doe, john@example.com', 'Jane Doe, jane@example.com', 'Jake Doe, jake@example.com', None],
        'Action': ['qa', 'sum', 'qa', None]}
df = pd.DataFrame(data)

# Step 1: Convert 'Timestamp' to datetime and drop invalid rows
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')  # Convert to datetime, coerce invalids to NaT
df = df.dropna(subset=['Timestamp'])  # Drop rows with invalid 'Timestamp'

# Step 2: Remove the time element (convert to date only) while keeping as datetime64[ns]
df['Timestamp'] = df['Timestamp'].dt.floor('d')  # Remove time component by flooring to the day

# Debug: Check processed DataFrame
print("Processed DataFrame (after removing time):")
print(df)

# Step 3: Get today's date without the time component (ensure it's datetime64[ns])
today = pd.Timestamp(datetime.now().strftime('%Y-%m-%d'))

# Debug: Print today's date and its type
print("\nToday's Date (without time):", today)
print("Type of 'today':", type(today))

# Step 4: Filter for today's data
df_today = df[df['Timestamp'] == today]

# Debug: Print filtered DataFrame
print("\nFiltered DataFrame for Today's Date:")
print(df_today)

# Step 5: Aggregated Stats
stats_till_date = df.groupby('Action').agg(
    Total_Requests=('Action', 'count'),
    Unique_Users=('User', lambda x: len(x.dropna().unique()))
).reset_index()

stats_today = df_today.groupby('Action').agg(
    Requests=('Action', 'count'),
    Unique_Users=('User', lambda x: len(x.dropna().unique()))
).reset_index()

# Debug: Print stats
print("\nStats Till Date:")
print(stats_till_date)

print("\nStats for Today:")
print(stats_today)
