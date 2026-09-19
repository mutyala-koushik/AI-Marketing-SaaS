from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from services.ai_service import (
    run_autonomous_retention_pipeline,
    run_ablation_comparison,
)

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


class AgentCampaignRequest(BaseModel):
    customer_segment: str
    churn_probability: float
    shap_features: Optional[List[Dict[str, Any]]] = []


class AblationRequest(BaseModel):
    customer_segment: str
    churn_probability: float


@router.post("/generate")
def generate_campaign_with_agent(
    payload: AgentCampaignRequest,
    db: Session = Depends(get_db),
):
    """
    Executes the 4-stage autonomous marketing agent pipeline:
    1. Diagnostician (SHAP telemetry analysis)
    2. Retriever (Vector policy grounding)
    3. Synthesis (Variant generation)
    4. Guardrail Judge (Automated compliance scoring)
    """
    try:
        pipeline_output = run_autonomous_retention_pipeline(
            customer_segment=payload.customer_segment,
            churn_probability=payload.churn_probability,
            shap_features=payload.shap_features or [],
        )

        # Persist campaign to database for history tracking
        campaign_data = pipeline_output.get("final_campaign", {})
        db_campaign = models.Campaign(
            campaign_name=campaign_data.get("campaign_name", "AI Retention Campaign"),
            target_segment=payload.customer_segment,
            variants=campaign_data.get("variants", []),
            compliance_score=pipeline_output.get("compliance_audit", {}).get(
                "compliance_score", 95
            ),
        )
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)

        return {
            "success": True,
            "campaign_id": db_campaign.id,
            "pipeline_telemetry": pipeline_output["stages"],
            "campaign": campaign_data,
            "compliance_audit": pipeline_output["compliance_audit"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline failure: {str(e)}")


@router.post("/ablation")
def compare_rag_ablation(payload: AblationRequest):
    """
    Viva / Research ablation endpoint:
    Compares raw ungrounded LLM output vs. RAG-grounded agent output.
    """
    try:
        comparison = run_ablation_comparison(
            customer_segment=payload.customer_segment,
            churn_probability=payload.churn_probability,
        )
        return {"success": True, "ablation_results": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ablation comparison failure: {str(e)}")


@router.get("/history")
def get_campaign_history(db: Session = Depends(get_db)):
    """Fetches previously synthesized and audited campaigns."""
    campaigns = db.query(models.Campaign).order_by(models.Campaign.id.desc()).limit(20).all()
    return campaigns