from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import pandas as pd

# Database dependency
from database.database import get_db
# Import your performance model if you have one defined:
# from models.campaign_performance import CampaignPerformance

router = APIRouter(prefix="/performance", tags=["Performance & ML"])

class CustomerRiskPayload(BaseModel):
    customer_id: str
    tenure: int = Field(..., ge=0)
    monthly_charges: float = Field(..., ge=0)
    total_charges: float = Field(..., ge=0)
    contract: str
    tech_support: str
    paperless_billing: str

# ==========================================
# 1. NEW ML & SHAP PREDICTION ENDPOINT
# ==========================================
@router.post("/evaluate-risk")
def evaluate_risk(data: CustomerRiskPayload, request: Request):
    try:
        ml = request.app.state.ml
        model = ml["model"]
        explainer = ml["explainer"]
        encoders = ml["encoders"]

        row = {
            "tenure": [data.tenure],
            "MonthlyCharges": [data.monthly_charges],
            "TotalCharges": [data.total_charges],
            "Contract": [encoders["Contract"].transform([data.contract])[0]],
            "TechSupport": [encoders["TechSupport"].transform([data.tech_support])[0]],
            "PaperlessBilling": [encoders["PaperlessBilling"].transform([data.paperless_billing])[0]],
        }
        df_row = pd.DataFrame(row)

        prob = float(model.predict_proba(df_row)[0][1])
        shap_values = explainer.shap_values(df_row)[0]
        feature_names = df_row.columns.tolist()

        drivers = [
            {"feature": feat, "attribution_score": round(float(val), 4)}
            for feat, val in zip(feature_names, shap_values) if val > 0
        ]
        drivers.sort(key=lambda x: x["attribution_score"], reverse=True)

        return {
            "customer_id": data.customer_id,
            "churn_probability": round(prob, 4),
            "risk_tier": "Critical" if prob > 0.65 else ("Moderate" if prob > 0.35 else "Low"),
            "causative_drivers": drivers[:3]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# 2. LEGACY GET BY ID ENDPOINT
# ==========================================
@router.get("/{performance_id}")
def get_performance_by_id(performance_id: int, db: Session = Depends(get_db)):
    # If fetching from an SQLAlchemy model:
    # record = db.query(CampaignPerformance).filter(CampaignPerformance.id == performance_id).first()
    # if not record:
    #     raise HTTPException(status_code=404, detail="Performance record not found")
    # return record
    return {
        "performance_id": performance_id,
        "status": "active",
        "metrics": {"clicks": 120, "conversions": 14}
    }