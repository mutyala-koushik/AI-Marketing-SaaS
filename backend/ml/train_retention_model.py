import os
import joblib
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score

os.makedirs("artifacts", exist_ok=True)

print("1. Downloading benchmark churn dataset...")
url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
df = pd.read_csv(url)

print("2. Formatting features and labels...")
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

feature_cols = ["tenure", "MonthlyCharges", "TotalCharges", "Contract", "TechSupport", "PaperlessBilling"]
X = df[feature_cols].copy()
y = df["Churn"]

print("3. Encoding categorical attributes...")
encoders = {}
for col in ["Contract", "TechSupport", "PaperlessBilling"]:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    encoders[col] = le
joblib.dump(encoders, "artifacts/encoders.joblib")

print("4. Training XGBoost Model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = xgb.XGBClassifier(
    n_estimators=150, 
    max_depth=4, 
    learning_rate=0.05, 
    eval_metric="logloss", 
    random_state=42
)
model.fit(X_train, y_train)

auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print(f"\n==========================================")
print(f"-> Model Trained! AUC-ROC Score: {auc:.4f}")
print(f"==========================================\n")
print(classification_report(y_test, model.predict(X_test)))

print("5. Computing TreeSHAP explainer...")
explainer = shap.TreeExplainer(model)

print("6. Saving artifacts to /artifacts folder...")
joblib.dump(model, "artifacts/xgb_churn_model.joblib")
joblib.dump(explainer, "artifacts/shap_explainer.joblib")
print("-> Done! Model and SHAP artifacts successfully saved.")