from typing import List

from pydantic import BaseModel, Field


class CampaignGenerationRequest(BaseModel):

    # =====================================================
    # PRODUCT / PERSONA
    # =====================================================

    product: str = Field(
        ...,
        min_length=2
    )

    persona: str = Field(
        ...,
        min_length=2
    )

    # =====================================================
    # CUSTOMER INTELLIGENCE
    # =====================================================

    characteristics: List[str] = Field(
        default_factory=list
    )

    marketing_needs: List[str] = Field(
        default_factory=list
    )

    preferred_approach: str = Field(
        default=""
    )

    # =====================================================
    # MARKETING STRATEGY
    # =====================================================

    marketing_goal: str = Field(
        ...,
        min_length=2
    )

    platform: str = Field(
        ...,
        min_length=2
    )

    budget: float = Field(
        ...,
        ge=0
    )

    campaign_type: str = Field(
        ...,
        min_length=2
    )

    content_format: str = Field(
        ...,
        min_length=2
    )

    marketing_angle: str = Field(
        ...,
        min_length=2
    )

    tone: str = Field(
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