from flask import Flask, render_template, request, url_for

import pandas as pd
from scripts.clean_water_data import load_and_clean_water_data
from scripts.clean_cancer_data import load_and_filter_bladder_cancer
from scripts.correlation_analysis import regional_correlation
import folium
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from scipy.stats import pearsonr
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def map_view():
   filepath = os.path.join("data", "UK water quality data.xlsx")
   df = load_and_clean_water_data(filepath) 


   if not {"lat", "lon", "pfas_sum", "name"}.issubset(df.columns):
       return "❌ Missing required columns in water data."


   # 🔹 Load ML model + feature columns
   try:
       import joblib
       clf = joblib.load("model/risk_classifier.pkl")
       expected_features = joblib.load("model/feature_names.pkl")


       # Prepare features and one-hot encode
       features = df[["pfas_sum", "matrix", "source_type"]].copy()
       features = pd.get_dummies(features)


       # Align columns with training features
       features = features.reindex(columns=expected_features, fill_value=0)


       # Predict risk class (0 = green, 1 = red)
       df["risk_class"] = clf.predict(features)
       df["color"] = df["risk_class"].map({0: "green", 1: "red"})
   except Exception as e:
       print(f"⚠️ ML model failed: {e}")
       df["color"] = "gray"


   # Convert to JSON-compatible dict
   data_for_map = df[["name", "lat", "lon", "pfas_sum", "color"]].to_dict(orient="records")


   # Load region data
   region_dict = {}
   try:
       region_df = pd.read_csv("cleaned_data/grouped_region_avg_pfas.csv")
       if "Region" in region_df.columns and "Mean_PFAS" in region_df.columns:
           region_df["Region"] = region_df["Region"].str.strip().str.lower()
           region_dict = region_df.set_index("Region")["Mean_PFAS"].to_dict()
   except Exception as e:
       print(f"⚠️ Could not load region PFAS data: {e}")


   # 🔍 Handle search query
   search_result = None
   if request.method == "POST":
       query = request.form.get("search", "").strip().lower()
       df["name_lower"] = df["name"].str.lower()
       match = df[df["name_lower"].str.contains(query)]


       if not match.empty:
           avg = round(match["pfas_sum"].mean(), 2)
           status = "High" if avg > 10 else "Low"
           search_result = {
               "area": match.iloc[0]["name"],
               "avg": avg,
               "status": status
           }
       else:
           search_result = {"error": "❌ No matching area found."}


   return render_template(
       "map.html",
       map_data=data_for_map,
       geojson_url=url_for("static", filename="UK_map.geojson"),
       region_pfas=region_dict,
       search_result=search_result
   )




@app.route("/cancer-analysis")
def cancer_analysis():
    # Load data
    water_path = "cleaned_data/grouped_region_avg_pfas.csv"
    cancer_path = "cleaned_data/uk_bladder_cancer_by_region.csv"
    water_df = pd.read_csv(water_path)
    cancer_df = pd.read_csv(cancer_path)



    # Average PFAS and cancer count
    avg_pfas = water_df["Mean_PFAS"].mean()
    cancer_count = cancer_df["Incidence"].sum()

    graphs = generate_cancer_analysis_graphs(water_df, cancer_df)
    print("✅ Graph keys generated:", graphs.keys())



    return render_template(
        "cancer_analysis.html",
        avg_pfas=round(avg_pfas, 2),
        cancer_count=int(cancer_count),
        correlation=graphs.get("correlation_r"),
        pval=graphs.get("correlation_pval"),
        graphs=graphs
    )

def generate_cancer_analysis_graphs(water_df, cancer_df):
    import matplotlib.pyplot as plt
    import io, base64
    from scipy.stats import pearsonr

    output = {}

    # Bladder cancer trend chart
    if 'Year' in cancer_df.columns:
        yearly_counts = cancer_df['Year'].value_counts().sort_index()
        fig2, ax2 = plt.subplots()
        ax2.plot(yearly_counts.index, yearly_counts.values, marker='o')
        ax2.set_title("Bladder Cancer Cases in London Over Time")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Number of Cases")
        ax2.set_xticks(yearly_counts.index[::2])
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png")
        buf2.seek(0)
        output["cancer_over_time"] = base64.b64encode(buf2.getvalue()).decode("utf-8")
        plt.close(fig2)

    # Correlation across regions
    if "Region" in water_df.columns and "Mean_PFAS" in water_df.columns:
        cancer_df["Region"] = cancer_df["Region"].str.strip().str.lower()
        regional_cancer = cancer_df.groupby("Region")["Incidence"].sum().reset_index()
        water_df["Region"] = water_df["Region"].str.strip().str.lower()

        merged_df = pd.merge(water_df, regional_cancer, on="Region")

        if len(merged_df) >= 2:
            r, pval = pearsonr(merged_df["Mean_PFAS"], merged_df["Incidence"])

            fig3, ax3 = plt.subplots()
            ax3.scatter(merged_df["Mean_PFAS"], merged_df["Incidence"], color="purple")
            ax3.set_xlabel("Mean PFAS")
            ax3.set_ylabel("Bladder Cancer Cases")
            ax3.set_title(f"Correlation: r = {round(r,3)}, p = {round(pval,4)}")
            for _, row in merged_df.iterrows():
                ax3.annotate(row["Region"].title(), (row["Mean_PFAS"], row["Incidence"]))
            buf3 = io.BytesIO()
            fig3.savefig(buf3, format="png")
            buf3.seek(0)
            output["correlation_plot"] = base64.b64encode(buf3.getvalue()).decode("utf-8")
            plt.close(fig3)

            output["correlation_r"] = round(r, 3)
            output["correlation_pval"] = round(pval, 4)

    return output



@app.route("/check", methods=["GET", "POST"])
def check_area():
    result = None
    if request.method == "POST":
        try:
            pfas_value = float(request.form.get("pfas_value", "").strip())

            if pfas_value <= 1:
                status = "✅ Safe (Low or no concern)"
                comment = "PFAS levels are within the considered safe range based on current guidelines."
            elif 1 < pfas_value <= 10:
                status = "⚠️ Moderate Concern"
                comment = "These PFAS levels may pose a long-term health risk with prolonged exposure."
            else:
                status = "❌ High Concern"
                comment = "This level of PFAS is above recommended safety thresholds and may increase cancer risk."

            result = {
                "value": round(pfas_value, 2),
                "status": status,
                "comment": comment
            }

        except ValueError:
            result = {"error": "Please enter a valid number."}

    return render_template("check.html", result=result)



@app.route("/education")
def education():
    

    region_data = []

    try:
        df = pd.read_csv("cleaned_data/region_avg_pfas_verified.csv")
        if "Region" in df.columns and "Mean_PFAS" in df.columns:
            df = df[df["Mean_PFAS"] > 10]  # Only show high-risk regions
            df = df[["Region", "Mean_PFAS"]]  # Ensure correct columns
            region_data = df.to_dict(orient="records")
    except Exception as e:
        print(f"⚠️ Could not load education PFAS data: {e}")

    return render_template("education.html", region_data=region_data)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
