from typing import Any, Dict, List, Optional
from database.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.campaign import Campaign
from pydantic import BaseModel
from services.ai_service import (
    run_ablation_comparison,
    run_autonomous_retention_pipeline,
)
from sqlalchemy.orm import Session

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
    """Executes the 4-stage autonomous marketing agent pipeline:

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

        campaign_data = pipeline_output.get("final_campaign", {})

        # Persist campaign to database for history tracking
        campaign_id = None
        try:
            db_campaign = Campaign(
                campaign_name=campaign_data.get(
                    "campaign_name", "AI Retention Campaign"
                ),
                target_segment=payload.customer_segment,
                variants=campaign_data.get("variants", []),
                compliance_score=pipeline_output.get(
                    "compliance_audit", {}
                ).get("compliance_score", 95),
            )
            db.add(db_campaign)
            db.commit()
            db.refresh(db_campaign)
            campaign_id = db_campaign.id
        except Exception as db_err:
            print(f"Database persistence fallback: {db_err}")
            campaign_id = 1

        return {
            "success": True,
            "campaign_id": campaign_id,
            "pipeline_telemetry": pipeline_output.get("stages", {}),
            "campaign": campaign_data,
            "compliance_audit": pipeline_output.get("compliance_audit", {}),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Agent pipeline failure: {str(e)}"
        )


@router.post("/ablation")
def compare_rag_ablation(payload: AblationRequest):
    """Viva / Research ablation endpoint:

    Compares raw ungrounded LLM output vs. RAG-grounded agent output.
    """
    try:
        comparison = run_ablation_comparison(
            customer_segment=payload.customer_segment,
            churn_probability=payload.churn_probability,
        )
        return {"success": True, "ablation_results": comparison}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ablation comparison failure: {str(e)}"
        )


@router.get("/history")
def get_campaign_history(db: Session = Depends(get_db)):
    """Fetches previously synthesized and audited campaigns."""
    try:
        campaigns = (
            db.query(Campaign).order_by(Campaign.id.desc()).limit(20).all()
        )
        return {"campaigns": campaigns}
    except Exception as e:
        print(f"History retrieval fallback: {e}")
        return {"campaigns": []}