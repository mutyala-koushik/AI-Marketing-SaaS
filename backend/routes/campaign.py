from fastapi import APIRouter, HTTPException

from models.campaign import CampaignGenerationRequest
from services.ai_service import generate_campaign_variants


router = APIRouter(
    prefix="/campaign",
    tags=["AI Campaign Generation"]
)


@router.post("/generate")
def generate_campaign(
    request: CampaignGenerationRequest
):
    """
    Generate 3 AI-powered campaign variants
    using the marketing strategy and customer intelligence.
    """

    try:

        result = generate_campaign_variants(
            product=request.product,
            persona=request.persona,
            marketing_goal=request.marketing_goal,
            platform=request.platform,
            budget=request.budget,
            campaign_type=request.campaign_type,
            content_format=request.content_format,
            marketing_angle=request.marketing_angle,
            tone=request.tone,
            call_to_action=request.call_to_action,
            recommended_offer=request.recommended_offer,

            # Customer Intelligence
            characteristics=request.characteristics,
            marketing_needs=request.marketing_needs,
            preferred_approach=request.preferred_approach,
        )

        return {
            "status": "success",
            "message": "Campaign variants generated.",
            "campaign": result
        }

    except ValueError as error:

        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"AI campaign generation failed: {str(error)}"
        )