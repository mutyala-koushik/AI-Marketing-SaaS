import json
import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

load_dotenv()


AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "mock",
).strip().lower()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "",
).strip()


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.7-flash",
).strip()


# =========================================================
# GEMINI CLIENT
# =========================================================

gemini_client = None


if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# HELPERS
# =========================================================

def _extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON from Gemini output.

    Handles:
    - Plain JSON
    - JSON inside ```json ... ``` blocks
    """

    text = text.strip()

    # -----------------------------------------------------
    # Remove markdown code fences
    # -----------------------------------------------------

    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # -----------------------------------------------------
    # Try direct JSON parsing
    # -----------------------------------------------------

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        # -------------------------------------------------
        # Try extracting JSON object
        # -------------------------------------------------

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:

            return json.loads(
                text[start:end + 1]
            )

        raise


def _normalize_hashtags(
    hashtags: Any,
) -> List[str]:
    """
    Normalize hashtags returned by Gemini.
    """

    if not isinstance(
        hashtags,
        list,
    ):
        return []

    result = []

    for tag in hashtags:

        tag = str(tag).strip()

        if not tag:
            continue

        if not tag.startswith("#"):
            tag = f"#{tag}"

        result.append(tag)

    return result[:8]


def _validate_campaign_variants(
    data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Validate and normalize Gemini campaign variants.

    Exactly 3 variants are required.
    """

    variants = data.get(
        "campaign_variants",
        [],
    )

    if not isinstance(
        variants,
        list,
    ):
        raise ValueError(
            "Gemini did not return campaign_variants."
        )

    normalized = []

    for index, variant in enumerate(
        variants[:3],
        start=1,
    ):

        if not isinstance(
            variant,
            dict,
        ):
            continue

        normalized.append(
            {
                "variant_id": variant.get(
                    "variant_id",
                    index,
                ),

                "style": str(
                    variant.get(
                        "style",
                        "General",
                    )
                ),

                "headline": str(
                    variant.get(
                        "headline",
                        "",
                    )
                ),

                "content": str(
                    variant.get(
                        "content",
                        "",
                    )
                ),

                "call_to_action": str(
                    variant.get(
                        "call_to_action",
                        "",
                    )
                ),

                "offer": str(
                    variant.get(
                        "offer",
                        "",
                    )
                ),

                "hashtags": _normalize_hashtags(
                    variant.get(
                        "hashtags",
                        [],
                    )
                ),
            }
        )

    if len(normalized) != 3:

        raise ValueError(
            "Gemini must return exactly 3 campaign variants."
        )

    return normalized


# =========================================================
# FACTUALITY / CLAIM VALIDATION
# =========================================================

FORBIDDEN_CLAIM_PATTERNS = [

    # -----------------------------------------------------
    # Community / relationship claims
    # -----------------------------------------------------

    "our community",
    "koushik community",
    "our inner circle",
    "member-only",
    "membership",
    "exclusive access",
    "exclusive membership",
    "join our community",
    "loyalty program",
    "reward program",

    # -----------------------------------------------------
    # Coaching / people claims
    # -----------------------------------------------------

    "personalized coach",
    "personalized fitness coach",
    "personal trainer",
    "ai coach",
    "certified trainer",
    "expert trainer",
    "dedicated coach",

    # -----------------------------------------------------
    # Social proof
    # -----------------------------------------------------

    "testimonials",
    "customer reviews",
    "thousands of customers",
    "millions of users",
    "millions of customers",
    "trusted by thousands",
    "trusted by millions",
    "customers love",
    "users love",

    # -----------------------------------------------------
    # Rankings / guarantees
    # -----------------------------------------------------

    "best in the world",
    "best fitness app",
    "number one",
    "#1 fitness app",
    "guaranteed results",
    "guaranteed",
    "proven results",
    "proven to work",

    # -----------------------------------------------------
    # Fake history / relationship
    # -----------------------------------------------------

    "since day one",
    "we've been with you",
    "we've been helping you",
    "we built this together",
    "you've been with us",
    "you have been with us",

    # -----------------------------------------------------
    # Unsupported offer modifiers
    # -----------------------------------------------------

    "limited-time",
    "limited time",
    "special deal",
    "special offer",
    "exclusive deal",
    "exclusive offer",
    "risk-free",
    "risk free",
    "act before it ends",
    "offer ends soon",
    "while supplies last",
    "secure this deal",
    "grab this deal",
    "claim your deal",

    # -----------------------------------------------------
    # Unsupported product capabilities
    # -----------------------------------------------------

    "tracking your progress",
    "track your progress",
    "progress tracking",
    "clear guidance",
    "personalized guidance",
    "personalized plan",
    "customized plan",
    "custom plan",
    "real-time tracking",
    "real time tracking",
    "smart recommendations",
    "personalized recommendations",

    # -----------------------------------------------------
    # Unsupported performance claims
    # -----------------------------------------------------

    "burn more calories",
    "lose weight fast",
    "lose weight quickly",
    "guaranteed fat loss",
    "guaranteed weight loss",
    "transform your body",
    "rapid results",
    "instant results",
]


def _find_unsupported_claims(
    text: str,
) -> List[str]:
    """
    Detect common unsupported claims in generated copy.
    """

    lowered = text.lower()

    found = []

    for pattern in FORBIDDEN_CLAIM_PATTERNS:

        if pattern.lower() in lowered:

            found.append(pattern)

    return found


def validate_campaign_factuality(
    variants: List[Dict[str, Any]],
    recommended_offer: str = "",
    call_to_action: str = "",
) -> Dict[str, Any]:
    """
    Validate generated campaign copy.

    Checks:

    1. Unsupported marketing claims
    2. Exact CTA preservation
    3. Exact offer preservation
    """

    issues = []

    for variant in variants:

        variant_id = variant.get(
            "variant_id"
        )

        headline = str(
            variant.get(
                "headline",
                "",
            )
        )

        content = str(
            variant.get(
                "content",
                "",
            )
        )

        offer = str(
            variant.get(
                "offer",
                "",
            )
        )

        variant_cta = str(
            variant.get(
                "call_to_action",
                "",
            )
        )

        # -------------------------------------------------
        # Combined content for claim checking
        # -------------------------------------------------

        text = " ".join(
            [
                headline,
                content,
                offer,
            ]
        )

        claims = _find_unsupported_claims(
            text
        )

        issue = {
            "variant_id": variant_id,
            "unsupported_claims": claims,
        }

        # -------------------------------------------------
        # EXACT OFFER VALIDATION
        # -------------------------------------------------

        if recommended_offer:

            if (
                offer.strip()
                != recommended_offer.strip()
            ):

                issue["offer_mismatch"] = {
                    "expected": recommended_offer,
                    "received": offer,
                }

        # -------------------------------------------------
        # EXACT CTA VALIDATION
        # -------------------------------------------------

        if call_to_action:

            if (
                variant_cta.strip()
                != call_to_action.strip()
            ):

                issue["cta_mismatch"] = {
                    "expected": call_to_action,
                    "received": variant_cta,
                }

        # -------------------------------------------------
        # Determine whether issue exists
        # -------------------------------------------------

        has_claim_issue = bool(
            issue["unsupported_claims"]
        )

        has_offer_issue = (
            "offer_mismatch" in issue
        )

        has_cta_issue = (
            "cta_mismatch" in issue
        )

        if (
            has_claim_issue
            or has_offer_issue
            or has_cta_issue
        ):

            issues.append(issue)

    return {
        "passed": len(issues) == 0,
        "issues": issues,
    }


# =========================================================
# GEMINI RETRY HELPER
# =========================================================

def _generate_gemini_with_retry(
    prompt: str,
    max_retries: int = 3,
) -> Any:
    """
    Call Gemini and retry temporary errors
    such as 503 and 429 using exponential backoff.
    """

    if gemini_client is None:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    last_error = None

    for attempt in range(
        max_retries + 1
    ):

        try:

            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            return response

        except Exception as error:

            last_error = error

            error_text = str(
                error
            ).lower()

            temporary_error = (
                "503" in error_text
                or "service unavailable" in error_text
                or "unavailable" in error_text
                or "429" in error_text
                or "resource exhausted" in error_text
                or "too many requests" in error_text
                or "rate limit" in error_text
            )

            # -------------------------------------------------
            # Permanent error
            # -------------------------------------------------

            if not temporary_error:
                raise

            # -------------------------------------------------
            # Final attempt
            # -------------------------------------------------

            if attempt >= max_retries:
                break

            # -------------------------------------------------
            # Exponential backoff
            #
            # 2 → 4 → 8 seconds
            # -------------------------------------------------

            wait_seconds = 2 ** (
                attempt + 1
            )

            print(
                "\n"
                "=================================================\n"
                "Gemini temporary error detected.\n"
                f"Attempt: {attempt + 1}/{max_retries + 1}\n"
                f"Retrying in {wait_seconds} seconds...\n"
                f"Error: {error}\n"
                "=================================================\n"
            )

            time.sleep(
                wait_seconds
            )

    raise ValueError(
        "Gemini is temporarily unavailable after "
        f"{max_retries + 1} attempts. "
        "Please try again shortly. "
        f"Last error: {last_error}"
    )


# =========================================================
# MOCK FALLBACK
# =========================================================

def generate_mock_campaigns(
    product: str,
    persona: str,
    marketing_goal: str,
    platform: str,
    budget: float,
    campaign_type: str,
    content_format: str,
    marketing_angle: str,
    tone: str,
    call_to_action: str,
    recommended_offer: str,
    characteristics: List[str] | None = None,
    marketing_needs: List[str] | None = None,
    preferred_approach: str = "",
) -> Dict[str, Any]:

    characteristics = (
        characteristics or []
    )

    marketing_needs = (
        marketing_needs or []
    )

    audience_context = {
        "persona": persona,
        "characteristics": characteristics,
        "marketing_needs": marketing_needs,
    }

    if preferred_approach:

        audience_context[
            "preferred_approach"
        ] = preferred_approach

    return {
        "provider": "mock",

        "audience_context":
            audience_context,

        "campaign_variants": [

            {
                "variant_id": 1,
                "style": "Emotional",

                "headline":
                    "Make Fitness a Simple Part of Your Day",

                "content":
                    (
                        f"Finding it difficult to stay "
                        f"consistent with fitness? "
                        f"{product} can help make your "
                        f"routine simpler and more manageable. "
                        f"Take the first step and build a "
                        f"healthier routine at your own pace. "
                        f"{recommended_offer}. "
                        f"{call_to_action}."
                    ),

                "call_to_action":
                    call_to_action,

                "offer":
                    recommended_offer,

                "hashtags": [
                    "#Fitness",
                    "#HealthyLifestyle",
                    "#FitZone",
                ],
            },

            {
                "variant_id": 2,
                "style": "Offer-Focused",

                "headline":
                    f"Start Your Fitness Journey with {product}",

                "content":
                    (
                        f"Ready to make your fitness "
                        f"journey easier? {product} offers "
                        f"a practical way to get started. "
                        f"Discover useful benefits without "
                        f"making your routine complicated. "
                        f"{recommended_offer}. "
                        f"{call_to_action}."
                    ),

                "call_to_action":
                    call_to_action,

                "offer":
                    recommended_offer,

                "hashtags": [
                    "#FitnessApp",
                    "#SpecialOffer",
                    "#StartToday",
                ],
            },

            {
                "variant_id": 3,
                "style": "Problem-Solution",

                "headline":
                    "Fitness Doesn't Have to Be Complicated",

                "content":
                    (
                        f"A busy routine can make it hard "
                        f"to stay consistent with fitness. "
                        f"{product} offers a simple way to "
                        f"bring fitness into your routine. "
                        f"Build healthier habits with a "
                        f"practical approach. "
                        f"{recommended_offer}. "
                        f"{call_to_action}."
                    ),

                "call_to_action":
                    call_to_action,

                "offer":
                    recommended_offer,

                "hashtags": [
                    "#FitnessGoals",
                    "#HealthyHabits",
                    "#WorkoutMotivation",
                ],
            },
        ],
    }


# =========================================================
# GEMINI CAMPAIGN GENERATION
# =========================================================

def generate_gemini_campaigns(
    product: str,
    persona: str,
    marketing_goal: str,
    platform: str,
    budget: float,
    campaign_type: str,
    content_format: str,
    marketing_angle: str,
    tone: str,
    call_to_action: str,
    recommended_offer: str,
    characteristics: List[str] | None = None,
    marketing_needs: List[str] | None = None,
    preferred_approach: str = "",
) -> Dict[str, Any]:

    # -----------------------------------------------------
    # Validate Gemini client
    # -----------------------------------------------------

    if gemini_client is None:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    characteristics = (
        characteristics or []
    )

    marketing_needs = (
        marketing_needs or []
    )

    # -----------------------------------------------------
    # Prepare customer intelligence
    # -----------------------------------------------------

    characteristics_text = "\n".join(
        f"- {item}"
        for item in characteristics
    )

    needs_text = "\n".join(
        f"- {item}"
        for item in marketing_needs
    )

    # =====================================================
    # BASE PROMPT
    # =====================================================

    base_prompt = f"""
You are an expert digital marketing strategist.

Generate exactly 3 high-quality campaign variants
for the following marketing campaign.

PRODUCT:
{product}

TARGET PERSONA:
{persona}

AUDIENCE CHARACTERISTICS:
{characteristics_text}

MARKETING NEEDS:
{needs_text}

PREFERRED APPROACH:
{preferred_approach}

MARKETING GOAL:
{marketing_goal}

PLATFORM:
{platform}

BUDGET:
{budget}

CAMPAIGN TYPE:
{campaign_type}

CONTENT FORMAT:
{content_format}

MARKETING ANGLE:
{marketing_angle}

TONE:
{tone}

CALL TO ACTION:
{call_to_action}

RECOMMENDED OFFER:
{recommended_offer}


=========================================================
STRICT OFFER RULE
=========================================================

Use the recommended offer EXACTLY as supplied.

The "offer" field in every campaign variant
MUST be identical to the supplied recommended offer.

Do NOT add words such as:

- limited-time
- limited time
- special
- exclusive
- risk-free
- risk free
- deal
- urgency
- scarcity

unless those words are explicitly present
inside the supplied recommended offer.


=========================================================
STRICT CTA RULE
=========================================================

Use the supplied call-to-action EXACTLY.

The "call_to_action" field in every variant
MUST be identical to the supplied CTA.


=========================================================
IMPORTANT RULES
=========================================================

1. Generate exactly 3 variants.

2. Use the audience characteristics and marketing needs
   as the actual basis for the messaging.

3. Translate audience characteristics into
   natural customer-facing marketing language.

4. Do NOT blindly repeat the internal persona name.

5. Do NOT expose technical terms such as:

   "customer segment"
   "marketing needs"
   "persona profile"
   "AI audience context"

6. Write natural customer-facing marketing content.

7. Keep each campaign specific to the supplied product.

8. Keep the requested tone.

9. Respect the requested marketing goal.

10. Respect the platform.

11. Use the supplied CTA exactly.

12. Use the supplied offer exactly.

13. Make every variant meaningfully different.

14. STRICT FACTUALITY:

You may ONLY use product features, offers,
benefits, communities, memberships, rewards,
discounts, prices, statistics, testimonials,
guarantees, or claims explicitly provided
in the input.

15. Never invent:

   - customer names
   - communities
   - loyalty programs
   - membership tiers
   - product features
   - personalized coaching
   - testimonials
   - social proof
   - performance results
   - discounts
   - prices
   - guarantees
   - exclusive access
   - relationships with customers

16. Do NOT create fictional relationships such as:

   "you've been with us since day one"
   "our community"
   "our inner circle"
   "we built this together"

17. Do NOT create unsupported urgency such as:

   "limited-time"
   "act now before it ends"
   "offer ends soon"
   "while supplies last"

18. Do NOT create unsupported risk claims such as:

   "risk-free"
   "guaranteed"
   "zero risk"

19. Do NOT create unsupported product capabilities such as:

   "progress tracking"
   "personalized plan"
   "personalized coaching"
   "AI coach"
   "real-time tracking"
   "smart recommendations"

20. Do NOT invent performance claims such as:

   "lose weight fast"
   "rapid results"
   "instant results"
   "guaranteed weight loss"

21. Do NOT copy the characteristics literally.

For example, do not write:

"customers with high spending"

or

"lower purchase frequency".

22. If a benefit is not explicitly provided,
describe the value generally rather than
inventing a specific feature.

23. The campaign must be possible to publish
using ONLY the supplied information.

24. Return ONLY valid JSON.

25. Do not include explanations outside JSON.


=========================================================
REQUIRED JSON STRUCTURE
=========================================================

Return exactly:

{{
  "campaign_variants": [
    {{
      "variant_id": 1,
      "style": "Emotional",
      "headline": "string",
      "content": "string",
      "call_to_action": "{call_to_action}",
      "offer": "{recommended_offer}",
      "hashtags": [
        "#tag1",
        "#tag2",
        "#tag3"
      ]
    }},
    {{
      "variant_id": 2,
      "style": "Offer-Focused",
      "headline": "string",
      "content": "string",
      "call_to_action": "{call_to_action}",
      "offer": "{recommended_offer}",
      "hashtags": [
        "#tag1",
        "#tag2",
        "#tag3"
      ]
    }},
    {{
      "variant_id": 3,
      "style": "Problem-Solution",
      "headline": "string",
      "content": "string",
      "call_to_action": "{call_to_action}",
      "offer": "{recommended_offer}",
      "hashtags": [
        "#tag1",
        "#tag2",
        "#tag3"
      ]
    }}
  ]
}}
"""

    # =====================================================
    # GENERATION + VALIDATION LOOP
    # =====================================================

    max_content_retries = 2

    last_validation = None

    for content_attempt in range(
        max_content_retries + 1
    ):

        # -------------------------------------------------
        # Start with base prompt
        # -------------------------------------------------

        prompt = base_prompt

        # -------------------------------------------------
        # Regeneration instructions
        # -------------------------------------------------

        if content_attempt > 0:

            unsupported = []

            if last_validation:

                for issue in last_validation.get(
                    "issues",
                    [],
                ):

                    unsupported.extend(
                        issue.get(
                            "unsupported_claims",
                            [],
                        )
                    )

            unsupported_text = ", ".join(
                sorted(
                    set(
                        unsupported
                    )
                )
            )

            prompt += f"""

=========================================================
REGENERATION REQUIRED
=========================================================

The previous campaign generation failed
factuality validation.

Detected unsupported claims:

{unsupported_text}

Generate ALL 3 variants again.

STRICT REQUIREMENTS:

1. Remove every detected unsupported claim.

2. Do NOT replace an unsupported claim
   with another invented claim.

3. Use ONLY information explicitly
   supplied in the input.

4. The "offer" field MUST be exactly:

"{recommended_offer}"

5. The "call_to_action" field MUST be exactly:

"{call_to_action}"

6. Do NOT add:

   - limited-time claims
   - urgency claims
   - scarcity claims
   - special deals
   - special offers
   - exclusive access
   - memberships
   - communities
   - testimonials
   - customer reviews
   - social proof
   - coaching
   - progress tracking
   - personalized plans
   - invented product features
   - invented discounts
   - invented prices
   - guarantees
   - performance results
   - risk-free claims

7. Do not modify the supplied offer.

8. Do not modify the supplied CTA.

9. Keep the campaigns natural and customer-facing.

10. Return ONLY valid JSON.
"""

        # -------------------------------------------------
        # Send request to Gemini
        # -------------------------------------------------

        response = _generate_gemini_with_retry(
            prompt=prompt,
            max_retries=3,
        )

        # -------------------------------------------------
        # Extract text
        # -------------------------------------------------

        text = response.text or ""

        if not text.strip():

            raise ValueError(
                "Gemini returned an empty response."
            )

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        parsed = _extract_json(
            text
        )

        # -------------------------------------------------
        # Validate campaign structure
        # -------------------------------------------------

        variants = _validate_campaign_variants(
            parsed
        )

        # -------------------------------------------------
        # Validate factuality
        # -------------------------------------------------

        validation = validate_campaign_factuality(
            variants=variants,
            recommended_offer=recommended_offer,
            call_to_action=call_to_action,
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        if validation["passed"]:

            return {
                "provider": "gemini",

                "audience_context": {
                    "persona": persona,
                    "characteristics": characteristics,
                    "marketing_needs": marketing_needs,
                    "preferred_approach":
                        preferred_approach,
                },

                "campaign_variants": variants,
            }

        # -------------------------------------------------
        # Validation failed
        # -------------------------------------------------

        last_validation = validation

        print(
            "\n"
            "=================================================\n"
            "CAMPAIGN FACTUALITY VALIDATION FAILED\n"
            f"Generation attempt: "
            f"{content_attempt + 1}/"
            f"{max_content_retries + 1}\n"
            f"Issues:\n"
            f"{json.dumps(validation['issues'], ensure_ascii=False, indent=2)}\n"
            "Regenerating campaigns...\n"
            "=================================================\n"
        )

    # =====================================================
    # ALL REGENERATION ATTEMPTS FAILED
    # =====================================================

    raise ValueError(
        "Generated campaign contains unsupported "
        "marketing claims or invalid offer/CTA "
        "after regeneration attempts: "
        + json.dumps(
            last_validation.get(
                "issues",
                [],
            )
            if last_validation
            else [],
            ensure_ascii=False,
        )
    )


# =========================================================
# PUBLIC FUNCTION
# =========================================================

def generate_openai_campaigns(
    product: str,
    persona: str,
    marketing_goal: str,
    platform: str,
    budget: float,
    campaign_type: str,
    content_format: str,
    marketing_angle: str,
    tone: str,
    call_to_action: str,
    recommended_offer: str,
    characteristics: List[str] | None = None,
    marketing_needs: List[str] | None = None,
    preferred_approach: str = "",
) -> Dict[str, Any]:
    """
    Backward-compatible public function.

    Existing routes can continue calling this function.

    Provider is selected using AI_PROVIDER.
    """

    # -----------------------------------------------------
    # Gemini
    # -----------------------------------------------------

    if AI_PROVIDER == "gemini":

        return generate_gemini_campaigns(
            product=product,
            persona=persona,
            marketing_goal=marketing_goal,
            platform=platform,
            budget=budget,
            campaign_type=campaign_type,
            content_format=content_format,
            marketing_angle=marketing_angle,
            tone=tone,
            call_to_action=call_to_action,
            recommended_offer=recommended_offer,
            characteristics=characteristics,
            marketing_needs=marketing_needs,
            preferred_approach=preferred_approach,
        )

    # -----------------------------------------------------
    # Mock provider
    # -----------------------------------------------------

    return generate_mock_campaigns(
        product=product,
        persona=persona,
        marketing_goal=marketing_goal,
        platform=platform,
        budget=budget,
        campaign_type=campaign_type,
        content_format=content_format,
        marketing_angle=marketing_angle,
        tone=tone,
        call_to_action=call_to_action,
        recommended_offer=recommended_offer,
        characteristics=characteristics,
        marketing_needs=marketing_needs,
        preferred_approach=preferred_approach,
    )


# =========================================================
# BACKWARD-COMPATIBLE ALIAS
# =========================================================

generate_campaign_variants = generate_openai_campaigns