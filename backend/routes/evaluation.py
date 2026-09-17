from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.content_evaluator import evaluate_campaign


router = APIRouter(
    prefix="/evaluation",
    tags=["Content Intelligence"]
)


class EvaluationRequest(BaseModel):

    product: str = Field(
        ...,
        min_length=2
    )

    persona: str = Field(
        ...,
        min_length=2
    )

    characteristics: list[str] = Field(
        ...,
        min_length=1
    )

    marketing_needs: list[str] = Field(
        ...,
        min_length=1
    )

    marketing_goal: str = Field(
        ...,
        min_length=2
    )

    platform: str = Field(
        ...,
        min_length=2
    )

    call_to_action: str = Field(
        ...,
        min_length=2
    )

    recommended_offer: str = Field(
        ...,
        min_length=2
    )

    campaign_variants: list[
        dict[str, Any]
    ] = Field(
        ...,
        min_length=3,
        max_length=3
    )


@router.post("/evaluate")
def evaluate_campaign_content(
    request: EvaluationRequest
):
    """
    Evaluate and rank campaign variants
    using customer intelligence and strategy.
    """

    try:

        result = evaluate_campaign(
            variants=request.campaign_variants,
            product=request.product,
            persona=request.persona,
            characteristics=request.characteristics,
            marketing_needs=request.marketing_needs,
            marketing_goal=request.marketing_goal,
            platform=request.platform,
            call_to_action=request.call_to_action,
            recommended_offer=request.recommended_offer
        )

        return {
            "status": "success",
            "message": "Campaign evaluation completed.",
            "persona": request.persona,
            "evaluation": result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Campaign evaluation failed: "
                f"{str(error)}"
            )
        )