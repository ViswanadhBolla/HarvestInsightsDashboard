import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Simulate 200 farms
n = 200
data = {
    'Farm_ID': np.arange(1, n+1),
    'Crop_Type': np.random.choice(['Wheat', 'Maize', 'Rice', 'Soybean'], size=n),
    'Soil_Moisture_%': np.random.uniform(10, 40, size=n).round(2),
    'Rainfall_mm': np.random.uniform(50, 300, size=n).round(1),
    'Avg_Temperature_C': np.random.uniform(15, 35, size=n).round(1),
    'Fertilizer_Used_kg_per_acre': np.random.uniform(50, 250, size=n).round(1),
    'Pest_Infestation': np.random.choice(['Yes', 'No'], size=n, p=[0.3, 0.7]),
    'Historical_Yield_ton_per_acre': np.random.uniform(1.5, 5.0, size=n).round(2)
}

# Create DataFrame
df = pd.DataFrame(data)

# Calculate Predicted Yield
df['Predicted_Yield_ton_per_acre'] = (
    df['Historical_Yield_ton_per_acre'] +
    (df['Soil_Moisture_%'] - 25) * 0.02 +
    (df['Rainfall_mm'] - 150) * 0.005 +
    (30 - abs(df['Avg_Temperature_C'] - 25)) * 0.05 -
    np.where(df['Pest_Infestation'] == 'Yes', 0.5, 0)
).round(2)

# Save to CSV
df.to_csv('harvest_insights_data.csv', index=False)

print("✅ Dataset created and saved as 'harvest_insights_data.csv'")
