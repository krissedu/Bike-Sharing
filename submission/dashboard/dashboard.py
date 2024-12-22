import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set style for seaborn plots
sns.set(style='dark')

# Function to create monthly rental data
def create_monthly_data(df):
    monthly_data = df.groupby('month').agg(
        total_rentals=('count', 'sum'),
        casual_rentals=('casual', 'sum'),
        registered_rentals=('registered', 'sum')
    ).reset_index()
    return monthly_data

# Function to filter data based on date range for scatter and bar plots
def create_weather_rentals_scatter(df, start_date, end_date):
    df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return df_filtered

# Function to create error analysis by day of the week
def create_error_by_day(df):
    data_mismatch = df[df['selisih_check'] == False].copy()
    data_mismatch['weekday'] = pd.to_datetime(data_mismatch['date']).dt.weekday + 1
    error_by_day = data_mismatch['weekday'].value_counts().sort_index()
    return error_by_day

# Try reading the CSV file with error handling
try:
    all_df = pd.read_csv("dashboard/all_data.csv")
except FileNotFoundError:
    st.error("The file 'all_data.csv' was not found!")
    st.stop()  # Stop execution if file is missing

# Convert date column to datetime
all_df['date'] = pd.to_datetime(all_df['date'])

# Extract min and max dates for date input range
min_date = all_df['date'].min()
max_date = all_df['date'].max()

# Sidebar for date range input
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT2AbN03HHQ_FUH1XUQftVHpyCDuU-oy_Tnew&s")
    
    # Date input for user to select range
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Convert start and end dates to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Check if start date is later than end date
if start_date > end_date:
    st.error("Start date cannot be later than end date.")
    st.stop()  # Stop execution if the date range is invalid

# Filter data based on the selected date range
def filter_data(start_date, end_date):
    return all_df[(all_df['date'] >= start_date) & (all_df['date'] <= end_date)]

main_df = filter_data(start_date, end_date)

# Generate monthly rental data
monthly_data = create_monthly_data(main_df)
df_filtered = create_weather_rentals_scatter(main_df, start_date, end_date)
error_by_day = create_error_by_day(main_df)

# Display the header
st.header('Bike Sharing Dashboard')

# Calculate and display key metrics
total_rentals = monthly_data['total_rentals'].sum()
casual_rentals = monthly_data['casual_rentals'].sum()
registered_rentals = monthly_data['registered_rentals'].sum()

# Display metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Rentals", total_rentals)

with col2:
    st.metric("Total Casual Rentals", casual_rentals)

with col3:
    st.metric("Total Registered Rentals", registered_rentals)

# Plot the rental data for the last year
st.subheader('Performa perentalan sepeda setahun terakhir')

plt.figure(figsize=(12, 6))
plt.plot(monthly_data['month'], monthly_data['total_rentals'], label='Total Rental', marker='o')
plt.plot(monthly_data['month'], monthly_data['casual_rentals'], label='Casual Rental', marker='o')
plt.plot(monthly_data['month'], monthly_data['registered_rentals'], label='Registered Rental', marker='o')
plt.xticks(range(1, 13))
plt.xlabel('Bulan')
plt.ylabel('Jumlah Rental')
plt.legend()
plt.grid()
st.pyplot(plt)

# Create scatter plots for weather conditions
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Temperatur vs Total Rental')
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='temp', y='count', data=df_filtered, alpha=0.6, label='Rentals')
    plt.xlabel('Temperatur')
    plt.ylabel('Total Rental')
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

with col2:
    st.subheader('Windspeed vs Total Rentals')
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='windspeed', y='count', data=df_filtered, alpha=0.6, label='Rentals')
    plt.xlabel('Wind Speed')
    plt.ylabel('Total Rental')
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

with col3:
    st.subheader('Kelembapan vs Total Rentals')
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='humidity', y='count', data=df_filtered, alpha=0.6, label='Rentals')
    plt.xlabel('Kelembapan')
    plt.ylabel('Total Rental')
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

# Bar plot for weather type vs total rentals
st.subheader('Rata-rata Total Rental vs Cuaca')

plt.figure(figsize=(10, 5))
sns.barplot(x='weather', y='count', data=df_filtered, errorbar='sd', hue='weather', legend=False, palette='coolwarm')
plt.xlabel('Cuaca')
plt.ylabel('Rata-rata Total Rental')
plt.xticks(ticks=[0, 1, 2, 3], labels=[
    'Clear/Few Clouds', 
    'Mist/Cloudy', 
    'Light Snow/Rain', 
    'Heavy Rain/Snow'
])
plt.tight_layout()
st.pyplot(plt)

# Pie chart for workday vs holiday rentals
st.subheader('Perentalan Workday vs Holiday')
st.markdown("""
Pie chart yang membandingkan persentase perentalan pada hari libur dan hari kerja 
""")

workday_counts = df_filtered.groupby('workingday')['count'].sum()
labels = ['Holiday', 'Workday']
colors = ['#ff9999', '#66b3ff']

workday_counts = workday_counts.reindex([0, 1], fill_value=0).fillna(0)

plt.figure(figsize=(8, 6))
plt.pie(workday_counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
st.pyplot(plt)

# Plot for error analysis by day
st.subheader('Hari dan Jumlah Kesalaahan')
st.markdown("""
Kesalahan yang dimaksud adalah perbedaan antara jumlah rental pada day_df dan jumlah rental pada hour_df, hal ini kemungkinan besar terjadi karena kelalaian penginput data.  
""")
plt.figure(figsize=(10, 6))
plt.plot(error_by_day.index, error_by_day.values, marker='o', linestyle='-', color='crimson')
plt.xticks(ticks=range(1, 8), labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
plt.xlabel('Hari dalam Seminggu')
plt.ylabel('Jumlah Kesalahan')
plt.grid(axis='y')
st.pyplot(plt)
