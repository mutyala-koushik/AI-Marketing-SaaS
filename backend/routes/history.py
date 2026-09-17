from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.campaign_history import CampaignHistory


router = APIRouter(
    prefix="/campaigns",
    tags=["Campaign History"],
)


class CampaignHistoryCreate(BaseModel):
    product: str
    persona: str
    platform: str
    marketing_goal: str
    variant_id: int
    style: str
    headline: str
    content: str
    call_to_action: str
    offer: str
    score: float | None = None
    status: str = "Ready to Launch"


@router.post("/history")
def create_campaign_history(
    campaign: CampaignHistoryCreate,
    db: Session = Depends(get_db),
):
    history = CampaignHistory(
        product=campaign.product,
        persona=campaign.persona,
        platform=campaign.platform,
        marketing_goal=campaign.marketing_goal,
        variant_id=campaign.variant_id,
        style=campaign.style,
        headline=campaign.headline,
        content=campaign.content,
        call_to_action=campaign.call_to_action,
        offer=campaign.offer,
        score=campaign.score,
        status=campaign.status,
        created_at=datetime.utcnow(),
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "status": "success",
        "message": "Campaign history saved.",
        "campaign": {
            "id": history.id,
            "product": history.product,
            "persona": history.persona,
            "platform": history.platform,
            "marketing_goal": history.marketing_goal,
            "variant_id": history.variant_id,
            "style": history.style,
            "headline": history.headline,
            "content": history.content,
            "call_to_action": history.call_to_action,
            "offer": history.offer,
            "score": history.score,
            "status": history.status,
            "created_at": history.created_at.isoformat(),
        },
    }


@router.get("/history")
def get_campaign_history(
    db: Session = Depends(get_db),
):
    records = (
        db.query(CampaignHistory)
        .order_by(
            CampaignHistory.created_at.desc()
        )
        .all()
    )

    return {
        "status": "success",
        "total": len(records),
        "campaigns": [
            {
                "id": item.id,
                "product": item.product,
                "persona": item.persona,
                "platform": item.platform,
                "marketing_goal": item.marketing_goal,
                "variant_id": item.variant_id,
                "style": item.style,
                "headline": item.headline,
                "content": item.content,
                "call_to_action": item.call_to_action,
                "offer": item.offer,
                "score": item.score,
                "status": item.status,
                "created_at": item.created_at.isoformat(),
            }
            for item in records
        ],
    }