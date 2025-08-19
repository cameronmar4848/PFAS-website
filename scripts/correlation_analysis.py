import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def regional_correlation(pfas_path, cancer_path):
    # Load regional PFAS averages
    pfas_df = pd.read_csv(pfas_path)
    pfas_df["Region"] = pfas_df["Region"].str.strip().str.lower()

    # Load and filter cancer data
    cancer_df = pd.read_csv(cancer_path)
    bladder_df = cancer_df[cancer_df["Tumour Type"].str.lower().str.contains("bladder", na=False)]
    bladder_df["Region"] = bladder_df["Region"].str.strip().str.lower()

    # Count cancer cases by region
    cancer_by_region = bladder_df.groupby("Region").size().reset_index(name="CancerCases")

    # Merge datasets
    merged_df = pd.merge(pfas_df, cancer_by_region, on="Region")

    if len(merged_df) >= 2:
        r, pval = pearsonr(merged_df["Mean_PFAS"], merged_df["CancerCases"])
    else:
        r, pval = None, None

    return round(r, 3) if r is not None else None, round(pval, 4) if pval is not None else None, merged_df

def generate_correlation_plot(df):
    plt.figure(figsize=(8, 6))
    plt.scatter(df["Mean_PFAS"], df["CancerCases"], color="blue")
    plt.title("Correlation between Regional PFAS and Bladder Cancer Cases")
    plt.xlabel("Average PFAS Level")
    plt.ylabel("Bladder Cancer Cases")
    plt.grid(True)

    for i, row in df.iterrows():
        plt.annotate(row["Region"].title(), (row["Mean_PFAS"], row["CancerCases"]), fontsize=8, alpha=0.7)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    plt.close()
    return encoded
