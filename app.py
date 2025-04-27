import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
data = pd.read_csv("harvest_insights_data.csv")

# Streamlit Page Configuration
st.set_page_config(page_title="Harvest Insights Dashboard", layout="wide")

# Dashboard Title
st.title(" Harvest Insights: Crop Yield Optimization Dashboard")

# Sidebar for Filters
st.sidebar.header(" Filter Data")
selected_crops = st.sidebar.multiselect(
    "Select Crop Type(s)",
    options=data["Crop_Type"].unique(),
    default=data["Crop_Type"].unique()
)
selected_pest = st.sidebar.selectbox(
    "Pest Infestation",
    options=["All", "Yes", "No"],
    index=0
)

# Filter Data
filtered_data = data[data["Crop_Type"].isin(selected_crops)]
if selected_pest != "All":
    filtered_data = filtered_data[filtered_data["Pest_Infestation"] == selected_pest]

# Display Metrics
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Avg Predicted Yield (ton/acre)", f"{filtered_data['Predicted_Yield_ton_per_acre'].mean():.2f}")
col2.metric("Avg Soil Moisture (%)", f"{filtered_data['Soil_Moisture_%'].mean():.2f}")
col3.metric("Avg Fertilizer Used (kg/acre)", f"{filtered_data['Fertilizer_Used_kg_per_acre'].mean():.1f}")

# Scatter Plot: Soil Moisture vs Predicted Yield
st.markdown("### Soil Moisture vs Predicted Yield")
fig_scatter = px.scatter(
    filtered_data,
    x="Soil_Moisture_%",
    y="Predicted_Yield_ton_per_acre",
    color="Crop_Type",
    trendline="ols",
    title="Soil Moisture vs Predicted Yield"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Bar Chart: Fertilizer Usage by Crop Type
st.markdown("###  Fertilizer Usage by Crop Type")
fig_bar = px.bar(
    filtered_data,
    x="Crop_Type",
    y="Fertilizer_Used_kg_per_acre",
    color="Crop_Type",
    title="Fertilizer Used per Crop Type",
    labels={"Fertilizer_Used_kg_per_acre": "Fertilizer (kg/acre)"},
    barmode="group"
)
st.plotly_chart(fig_bar, use_container_width=True)

# Histogram: Distribution of Predicted Yields
st.markdown("###  Predicted Yield Distribution")
fig_hist = px.histogram(
    filtered_data,
    x="Predicted_Yield_ton_per_acre",
    nbins=20,
    title="Distribution of Predicted Crop Yields",
    labels={"Predicted_Yield_ton_per_acre": "Yield (ton/acre)"}
)
st.plotly_chart(fig_hist, use_container_width=True)

# Expandable Raw Data Section
with st.expander(" View Raw Data"):
    st.dataframe(filtered_data)
