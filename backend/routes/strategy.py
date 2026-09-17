from fastapi import APIRouter

from models.strategy import StrategyRequest
from services.strategy_engine import generate_strategy


router = APIRouter(
    prefix="/strategy",
    tags=["Marketing Strategy"]
)


@router.post("/generate")
def generate_marketing_strategy(request: StrategyRequest):
    """
    Generate an explainable marketing strategy
    using customer intelligence and business inputs.
    """

    strategy = generate_strategy(
        product=request.product,
        persona=request.persona,
        marketing_goal=request.marketing_goal,
        platform=request.platform,
        budget=request.budget,
        preferred_tone=request.preferred_tone
    )

    return {
        "status": "success",
        "message": "Marketing strategy generated.",
        "strategy": strategy
    }