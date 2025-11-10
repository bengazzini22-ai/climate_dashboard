# app.py - Climate Impact Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Climate Impact Dashboard", layout="wide")
st.title("🌍 Climate Impact Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("data/merged_energy_temp.csv")

try:
    df = load_data()
    # Convert °C anomalies to °F anomalies (difference only × 1.8)
    df['temp_anomaly_f'] = df['temp_anomaly'] * 1.8
except FileNotFoundError:
    st.error("Merged data not found. Run: python scripts/clean_merge_data.py")
    st.stop()

st.write("### Sample Data Preview")
st.dataframe(df.head())

# --- Section 1: Scatter Plot (Energy per Capita vs Temp Anomaly) ---
st.subheader("⚡ Energy Use vs Temperature Anomaly (°F)")

year = st.slider("Select year", int(df['year'].min()), int(df['year'].max()), 2020)
dfy = df[(df['year'] == year) & df['energy_per_capita'].notna() & df['temp_anomaly_f'].notna()]

if dfy.empty:
    st.warning("No data available for the selected year.")
else:
    fig1 = px.scatter(
        dfy,
        x='energy_per_capita',
        y='temp_anomaly_f',
        hover_name='country',
        title=f"Energy Use per Capita vs Temperature Anomaly ({year})",
        labels={
            'energy_per_capita': 'Energy Use per Capita (kWh/person)',
            'temp_anomaly_f': 'Temperature Anomaly (°F)'
        }
    )
    st.plotly_chart(fig1, use_container_width=True)

# --- Section 2: Line Chart (Global averages over time) ---
st.subheader("📈 Global Trends Over Time (°F & Renewable Share)")

global_trends = df.groupby('year')[['temp_anomaly_f', 'renewables_share_energy']].mean().reset_index()

fig2 = px.line(
    global_trends,
    x='year',
    y=['temp_anomaly_f', 'renewables_share_energy'],
    labels={
        'value': 'Value',
        'year': 'Year',
        'variable': 'Metric'
    },
    title="Global Temperature Anomaly (°F) vs Renewable Energy Share (1990–2023)"
)
st.plotly_chart(fig2, use_container_width=True)

# --- Section 3: Choropleth Map ---
st.subheader("🗺️ Global Temperature Anomalies Map (°F)")

map_year = st.slider("Select map year", int(df['year'].min()), int(df['year'].max()), 2020, key="map_year")
df_map = df[(df['year'] == map_year) & df['temp_anomaly_f'].notna()]

if df_map.empty:
    st.warning("No temperature data available for the selected year.")
else:
    fig3 = px.choropleth(
        df_map,
        locations='iso_code',
        color='temp_anomaly_f',
        hover_name='country',
        title=f"Global Temperature Anomalies ({map_year}, °F)",
        color_continuous_scale="RdYlBu_r",
        range_color=(df_map['temp_anomaly_f'].min(), df_map['temp_anomaly_f'].max()),
    )
    fig3.update_geos(showcountries=True, showcoastlines=True, projection_type="natural earth")
    st.plotly_chart(fig3, use_container_width=True)

# --- Footer / Summary ---
st.markdown("""
---
 **Tips for presenting:**
- The **scatter plot** shows how higher energy consumption per person often correlates with increased temperature anomalies (in °F).  
- The **line chart** tracks the rise in global temperature anomalies vs renewable energy growth.  
- The **map** provides a clear global view of warming patterns by country.  
""")