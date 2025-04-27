import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import plotly.express as px

# ---------------------- Simulated Data Loader ----------------------
@st.cache_data(show_spinner=False)
def load_simulated_data():
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'Farm_ID': np.arange(1, n+1),
        'Crop_Type': np.random.choice(['Wheat','Maize','Rice','Soybean'], n),
        'Soil_Moisture_%': np.random.uniform(10,40,n).round(2),
        'Rainfall_mm': np.random.uniform(50,300,n).round(1),
        'Avg_Temperature_C': np.random.uniform(15,35,n).round(1),
        'Fertilizer_Used_kg_per_acre': np.random.uniform(50,250,n).round(1),
        'Pest_Infestation': np.random.choice(['Yes','No'], n, p=[0.3,0.7]),
        'Historical_Yield_ton_per_acre': np.random.uniform(1.5,5.0,n).round(2)
    })
    df['Predicted_Yield_ton_per_acre'] = (
        df['Historical_Yield_ton_per_acre'] +
        (df['Soil_Moisture_%'] - 25)*0.02 +
        (df['Rainfall_mm'] - 150)*0.005 +
        (30 - abs(df['Avg_Temperature_C'] - 25))*0.05 -
        np.where(df['Pest_Infestation']=='Yes', 0.5, 0)
    ).round(2)
    return df

# ---------------------- USDA NASS QuickStats Loader ----------------------
@st.cache_data(show_spinner=False)
def load_nass_data(key, commodity="CORN", state="ALL", agg_level="STATE", statistic="YIELD", year_range=(2015,2020)):
    base_url = "https://quickstats.nass.usda.gov/api/api_GET"
    rows = []
    for yr in range(year_range[0], year_range[1]+1):
        params = {
            "key": key,
            "commodity_desc": commodity,
            "year": yr,
            "agg_level_desc": agg_level,
            "statisticcat_desc": statistic,
            "format": "JSON"
        }
        if state != "ALL":
            params["state_alpha"] = state
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            rows.extend(resp.json().get("data", []))
        except requests.exceptions.RequestException:
            continue
    df = pd.DataFrame(rows)
    if "Value" in df.columns:
        df["Value"] = pd.to_numeric(df["Value"].str.replace(",", ""), errors='coerce')
    if 'year' in df.columns:
        df['year'] = df['year'].astype(int)
    return df

# ---------------------- Streamlit App ----------------------
st.set_page_config(page_title="Harvest Insights Dashboard", layout="wide")
st.title("Harvest Insights: Crop Yield Optimization")

# Sidebar: Data Source Selection
source = st.sidebar.radio("Select Data Source:", ["Simulated", "USDA NASS"])
if source == "Simulated":
    data = load_simulated_data()

elif source == "USDA NASS":
    comm = st.sidebar.selectbox("Commodity Desc:", ["CORN", "WHEAT", "SOYBEANS", "RICE"])
    state = st.sidebar.selectbox("State:", ["ALL", "VA", "CA", "TX", "IA"])
    agg = st.sidebar.selectbox("Aggregation Level:", ["STATE", "COUNTY"])
    yr1, yr2 = st.sidebar.slider("Year Range:", 2010, 2024, (2015, 2020))
    key = st.secrets.get("NASS_API_KEY", "")
    if not key:
        st.error("🔑 USDA NASS API key missing. Add to .streamlit/secrets.toml or env var.")
        st.stop()
    data = load_nass_data(
        key=key,
        commodity=comm,
        state=state,
        agg_level=agg,
        statistic="YIELD",
        year_range=(yr1, yr2)
    )

# Convert dates
for col in data.columns:
    if 'date' in col.lower():
        data[col] = pd.to_datetime(data[col], errors='ignore')

# ---------------------- Key Metrics ----------------------
st.markdown("### Key Metrics")
cols = st.columns(3)
if source == "Simulated":
    cols[0].metric("Avg Predicted Yield", f"{data['Predicted_Yield_ton_per_acre'].mean():.2f}")
    cols[1].metric("Avg Rainfall (mm)", f"{data['Rainfall_mm'].mean():.1f}")
    cols[2].metric("Avg Temp (°C)", f"{data['Avg_Temperature_C'].mean():.1f}")
else:
    avg_val = data['Value'].mean() if 'Value' in data.columns else None
    years = data['year'].nunique() if 'year' in data.columns else None
    cols[0].metric("Avg Value", f"{avg_val:,.0f}" if avg_val else "N/A")
    cols[1].metric("Period", f"{yr1}–{yr2}")
    cols[2].metric("Records", len(data))

# ---------------------- Enhanced Dashboard ----------------------
st.markdown("## Exploratory Insights")
# Correlation matrix for numeric features
num_cols = data.select_dtypes('number').columns.tolist()
if len(num_cols) > 1:
    st.markdown("### Feature Correlation Matrix")
    corr = data[num_cols].corr()
    fig_corr = px.imshow(corr, title="Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)

# Category-based distributions
if source == "Simulated" and 'Crop_Type' in data.columns:
    st.markdown("### Yield Distribution by Crop Type")
    fig_box = px.box(
        data, x='Crop_Type', y='Predicted_Yield_ton_per_acre',
        title="Predicted Yield by Crop"
    )
    st.plotly_chart(fig_box, use_container_width=True)
elif source == "USDA NASS" and 'state_alpha' in data.columns:
    st.markdown("### Value Distribution by State")
    fig_box2 = px.box(
        data, x='state_alpha', y='Value',
        title="Value by State"
    )
    st.plotly_chart(fig_box2, use_container_width=True)

# Time-series or top lists for USDA NASS
if source == "USDA NASS" and not data.empty:
    st.markdown("### Average Yield Over Time")
    df_year = data.groupby('year')['Value'].mean().reset_index()
    fig_ts = px.line(
        df_year, x='year', y='Value',
        title="Avg Yield by Year"
    )
    st.plotly_chart(fig_ts, use_container_width=True)

# ---------------------- Raw Data & Download ----------------------
with st.expander("View Raw Data"):
    st.dataframe(data)
csv = data.to_csv(index=False)
st.sidebar.download_button("Download Data as CSV", data=csv, file_name="harvest_insights_data.csv")
