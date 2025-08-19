import pandas as pd


def load_and_filter_bladder_cancer(filepath):
    df = pd.read_excel(filepath, header=1)
    print("✅ Loaded cancer data. Columns:", df.columns.tolist())

    # Preview first few rows
    print(df.head(3))

    # Make sure column names are what we expect
    if 'Region' in df.columns and 'Tumour Type' in df.columns:
        # Step 1: Filter for 'Bladder' only
        df = df[df['Tumour Type'].str.contains("Bladder", case=False, na=False)]

        # Step 2: Filter for rows with 'London' in Region
        df = df[df['Region'].str.contains("London", case=False, na=False)]

        print(f"🎯 Filtered rows: {len(df)}")
        print(df[['Region', 'Tumour Type']].head())

        # Save to CSV for use in Flask
        df.to_csv("data/London_cancer_data.csv", index=False)
        print("💾 Saved filtered cancer data to data/London_cancer_data.csv")

        return df
    else:
        print("❌ Required columns not found.")
        return pd.DataFrame()

    
def filter_london_bladder_cancer(df):
    if 'Region' in df.columns and 'Tumour Type' in df.columns:
        london_df = df[df['Region'].str.contains("London", case=False, na=False)]
        bladder_df = london_df[london_df['Tumour Type'].str.contains("Bladder", case=False, na=False)]
        print(f"🎯 Filtered bladder cancer cases in London: {len(bladder_df)}")
        return bladder_df
    else:
        print("❌ Required columns not found in cancer data.")
        return pd.DataFrame()
