# machine_learning_model.py
# This script trains a machine learning classifier to predict water site risk

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# --- Load and Clean Data ---
df = pd.read_excel("data/UK water quality data.xlsx")

# --- Define Risk Label (Weak Supervision) ---
df = df[df["pfas_sum"].notna()]  # Ensure PFAS data is available
df["risk_label"] = (df["pfas_sum"] > 10).astype(int)

# --- Choose Features ---
features = ["pfas_sum", "year", "matrix", "source_type", "type"]
df = df.dropna(subset=features)
X = pd.get_dummies(df[features])
y = df["risk_label"]

# --- Split and Train ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# --- Evaluate ---
y_pred = clf.predict(X_test)
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# --- Save Model and Feature Columns ---
joblib.dump(clf, "model/risk_classifier.pkl")
joblib.dump(X.columns.tolist(), "model/feature_columns.pkl")
print("✅ Model and feature columns saved.")
# Save feature names used during training
joblib.dump(X.columns.tolist(), "model/feature_names.pkl")
