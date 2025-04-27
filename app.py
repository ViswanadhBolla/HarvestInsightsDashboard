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

# Add Date Range Filter
if "Date" in data.columns:
    st.sidebar.header("Date Range")
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=[data["Date"].min(), data["Date"].max()]
    )
    filtered_data = filtered_data[
        (filtered_data["Date"] >= pd.to_datetime(start_date)) &
        (filtered_data["Date"] <= pd.to_datetime(end_date))
    ]

# Display Metrics
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
# Tooltips for Metrics
col1.metric("Avg Predicted Yield (ton/acre)", f"{filtered_data['Predicted_Yield_ton_per_acre'].mean():.2f}", "Average yield predicted per acre")
col2.metric("Avg Soil Moisture (%)", f"{filtered_data['Soil_Moisture_%'].mean():.2f}", "Average soil moisture percentage")
col3.metric("Avg Fertilizer Used (kg/acre)", f"{filtered_data['Fertilizer_Used_kg_per_acre'].mean():.1f}", "Average fertilizer used per acre")

# Dynamic Scatter Plot
st.markdown("### Custom Scatter Plot")
x_axis = st.selectbox("Select X-axis", options=filtered_data.columns, index=filtered_data.columns.get_loc("Soil_Moisture_%"))
y_axis = st.selectbox("Select Y-axis", options=filtered_data.columns, index=filtered_data.columns.get_loc("Predicted_Yield_ton_per_acre"))
fig_custom_scatter = px.scatter(
    filtered_data,
    x=x_axis,
    y=y_axis,
    color="Crop_Type",
    trendline="ols",
    title=f"{x_axis} vs {y_axis}"
)
st.plotly_chart(fig_custom_scatter, use_container_width=True)

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

# Dataset Summary
st.sidebar.markdown("### Dataset Summary")
st.sidebar.write(f"Total Records: {len(data)}")
st.sidebar.write(f"Unique Crop Types: {data['Crop_Type'].nunique()}")
if "Date" in data.columns:
    st.sidebar.write(f"Date Range: {data['Date'].min()} to {data['Date'].max()}")

# Download Filtered Data
st.sidebar.markdown("### Download Data")
csv = filtered_data.to_csv(index=False)
st.sidebar.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)
