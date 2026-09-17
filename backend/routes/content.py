from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
import os

router = APIRouter(prefix="/content", tags=["Content Synthesis"])

class GenerationPayload(BaseModel):
    customer_id: str
    churn_probability: float
    causative_drivers: list[dict]

class RetentionCampaignOutput(BaseModel):
    headline: str
    personalized_copy: str
    incentive_offer: str
    driver_neutralized: str
    image_prompt: str
    image_url: str | None = None

@router.post("/synthesize-retention", response_model=RetentionCampaignOutput)
def synthesize_retention(payload: GenerationPayload):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    drivers_str = ", ".join([f"{d['feature']} (Score: +{d['attribution_score']})" for d in payload.causative_drivers])
    
    prompt = f"""
    You are an automated CRM retention visual designer and copywriter.
    Customer: {payload.customer_id}
    Churn Risk: {payload.churn_probability * 100:.1f}%
    Top Risk Factors Identified by TreeSHAP: {drivers_str}

    Tasks:
    1. Write a targeted retention pitch that directly resolves these friction points.
    2. Write a descriptive, photorealistic ad banner image prompt designed to neutralize this exact churn reason visually (e.g. happy customer receiving dedicated onboarding assistance, or a modern dashboard highlighting billing savings).

    Do not mention machine learning, SHAP, models, or algorithms.
    """

    try:
        # 1. Generate Structured Copy + Targeted Visual Prompt
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": RetentionCampaignOutput,
                "temperature": 0.2
            }
        )
        campaign = RetentionCampaignOutput.model_validate_json(response.text)

        # 2. Generate Visual Creative Banner (via Imagen 3)
        try:
            image_result = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=campaign.image_prompt,
                config=dict(
                    number_of_images=1,
                    aspect_ratio="16:9",
                    output_mime_type="image/jpeg",
                ),
            )
            for generated_image in image_result.generated_images:
                # Store as base64 data URI for instant dashboard rendering
                import base64
                encoded_bytes = base64.b64encode(generated_image.image.image_bytes).decode("utf-8")
                campaign.image_url = f"data:image/jpeg;base64,{encoded_bytes}"
        except Exception as img_err:
            print(f"Image generation fallback: {img_err}")
            # Fallback to high-quality contextual Unsplash placeholder if image quota is unavailable
            campaign.image_url = "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80"

        return campaign
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))