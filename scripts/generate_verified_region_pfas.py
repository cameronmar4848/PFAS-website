import pandas as pd

# Load the site-to-region mapping
site_region_df = pd.read_csv("data/site_to_region.csv")  # Make sure this file exists

# Load the full PFAS water data
water_df = pd.read_excel("data/UK water quality data.xlsx")

# Merge on site name
merged_df = pd.merge(site_region_df, water_df, left_on="Site", right_on="name")

# Optional: Cap PFAS values to remove outliers
merged_df["pfas_sum_capped"] = merged_df["pfas_sum"].clip(upper=100)  # You can change 100 if needed

# Group by region and calculate the average of capped values
region_avg_df = (
    merged_df.groupby("Region")["pfas_sum_capped"]
    .mean()
    .reset_index()
    .rename(columns={"Region": "Region", "pfas_sum_capped": "Mean_PFAS"})
    .sort_values("Mean_PFAS", ascending=False)
)

# Save to CSV
region_avg_df.to_csv("cleaned_data/region_avg_pfas_verified.csv", index=False)
print("✅ Saved cleaned_data/region_avg_pfas_verified.csv")
