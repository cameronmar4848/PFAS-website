import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.clean_cancer_data import load_and_filter_bladder_cancer

def preprocess_and_save():
    cleaned_df = load_and_filter_bladder_cancer("data/cancer_stats.xlsx")
    if not cleaned_df.empty:
        cleaned_df.to_csv("data/London_cancer_data_cleaned.csv", index=False)
        print("✅ Cleaned cancer data saved.")
    else:
        print("⚠️ No data saved — empty after cleaning.")

if __name__ == "__main__":
    preprocess_and_save()
