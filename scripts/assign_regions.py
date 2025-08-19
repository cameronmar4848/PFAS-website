import pandas as pd

# Define bounding boxes for UK regions based on cancer data grouping
region_boxes = {
    "london": [51.30, 51.70, -0.5, 0.3],
    "south": [50.1, 51.7, -5.5, 0.9],  # South West + South East
    "midlands": [52.2, 53.5, -3.0, 0.2],  # West + East Midlands + East of England
    "north": [53.3, 55.8, -3.3, -0.5],  # North East + North West + Yorkshire
}

# Load original PFAS water data
water_df = pd.read_excel("data/UK water quality data.xlsx")

# Clean relevant columns
water_df = water_df[["name", "lat", "lon", "pfas_sum"]].copy()

assigned = []

for _, row in water_df.iterrows():
    lat, lon = row["lat"], row["lon"]
    site_name, pfas = row["name"], row["pfas_sum"]

    region = None
    for reg, (lat_min, lat_max, lon_min, lon_max) in region_boxes.items():
        if pd.notna(lat) and pd.notna(lon):
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                region = reg
                break

    if region:
        assigned.append({"Region": region, "Site": site_name, "PFAS": pfas})

# Convert to DataFrame
region_df = pd.DataFrame(assigned)

# Group by region and calculate average PFAS
avg_pfas_by_region = region_df.groupby("Region")["PFAS"].mean().reset_index()
avg_pfas_by_region.columns = ["Region", "Mean_PFAS"]

# Save to file
avg_pfas_by_region.to_csv("cleaned_data/grouped_region_avg_pfas.csv", index=False)
print("✅ grouped_region_avg_pfas.csv saved to /cleaned_data")
