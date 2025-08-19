import pandas as pd

# ✅ Correct method for Excel
df = pd.read_excel("data/cancer_stats.xlsx", header=1)

# Continue with cleaning...
df["Tumour Type"] = df["Tumour Type"].str.strip().str.lower()
df["Region"] = df["Region"].str.strip().str.lower()

bladder_df = df[df["Tumour Type"] == "bladder"]
bladder_df = bladder_df.dropna(subset=["Region", "Incidence"])
bladder_df["Incidence"] = pd.to_numeric(bladder_df["Incidence"], errors="coerce")

regional_cancer = bladder_df.groupby("Region")["Incidence"].sum().reset_index()
regional_cancer.to_csv("cleaned_data/uk_bladder_cancer_by_region.csv", index=False)
print("✅ Saved: cleaned_data/uk_bladder_cancer_by_region.csv")

