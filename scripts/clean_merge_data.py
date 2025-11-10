# scripts/clean_merge_data.py
import pandas as pd
import os

# === Paths ===
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
ENERGY_CSV = os.path.join(DATA_DIR, 'owid-energy-data.csv')
TEMP_CSV = os.path.join(DATA_DIR, 'temperature_data.csv')
OUTPUT_CSV = os.path.join(DATA_DIR, 'merged_energy_temp.csv')

print("Loading energy data from:", ENERGY_CSV)
energy = pd.read_csv(ENERGY_CSV)
print("Energy rows:", len(energy))

print("Loading temperature data from:", TEMP_CSV)
temp = pd.read_csv(TEMP_CSV)
print("Temperature rows:", len(temp))

# --- Normalize temperature columns if needed ---
if 'country' not in temp.columns:
    if 'Entity' in temp.columns:
        temp = temp.rename(columns={'Entity': 'country'})
if 'year' not in temp.columns and 'Year' in temp.columns:
    temp = temp.rename(columns={'Year': 'year'})

# Expect a column named 'temp_anomaly' (°C since 1990)
if 'temp_anomaly' not in temp.columns:
    print("WARNING: 'temp_anomaly' column not found in temperature CSV.")
    print("Columns found:", list(temp.columns))
    raise ValueError("Please ensure the temperature CSV contains a 'temp_anomaly' column.")

# Keep only the required columns
temp = temp[['country', 'year', 'temp_anomaly']]
temp['year'] = temp['year'].astype(int)

# Limit to 1990-2023
temp = temp[temp['year'].between(1990, 2023)]

# Merge datasets on country + year
merged = energy.merge(temp, on=['country', 'year'], how='left')

# Save merged file
merged.to_csv(OUTPUT_CSV, index=False)
print("\n✅ Merged dataset saved to:", OUTPUT_CSV)
print("Merged rows:", len(merged))
