import pandas as pd
import os

def combine_pfas_and_cancer():
    # Load PFAS region data
    pfas_path = os.path.join("cleaned_data", "region_avg_pfas.csv")
    pfas_df = pd.read_csv(pfas_path)

    # Load cancer data (London + other regions)
    cancer_path = os.path.join("data", "London_cancer_data_cleaned.csv")
    cancer_df = pd.read_csv(cancer_path)

    # Filter to bladder cancer only
    cancer_df = cancer_df[cancer_df["Tumour Type"].str.lower() == "bladder"]

    # Group by Region, summing incidence counts
    region_cancer = (
        cancer_df.groupby("Region")["Incidence"]
        .sum()
        .reset_index()
        .rename(columns={"Incidence": "Total_Bladder_Cases"})
    )

    # Merge with PFAS regional averages
    merged = pd.merge(pfas_df, region_cancer, on="Region", how="inner")

    # Save to file
    output_path = os.path.join("cleaned_data", "pfas_vs_cancer_by_region.csv")
    merged.to_csv(output_path, index=False)
    print(f"✅ Combined dataset saved to: {output_path}")
    print(merged)

if __name__ == "__main__":
    combine_pfas_and_cancer()
