from services.persona_profiles import get_persona_profile


def interpret_segment(segment):
    """
    Convert a numerical customer segment into
    a meaningful marketing persona and characteristics.
    """

    income = segment["average_income"]
    purchase_frequency = segment["average_purchase_frequency"]
    spend = segment["average_spend"]

    # --------------------------------------------------
    # High-value loyal customers
    # --------------------------------------------------

    if (
        income >= 70000
        and purchase_frequency >= 10
        and spend >= 6000
    ):
        persona = "High-Value Loyal Customers"

        result = {
            "persona": persona,
            "description": (
                "Customers with high spending, frequent purchases "
                "and strong engagement."
            ),
            "marketing_goal": "Retention and upselling",
            "recommended_strategy": (
                "Use loyalty rewards, premium offers and "
                "exclusive benefits."
            ),
            "recommended_content": (
                "Premium-focused messaging, loyalty benefits "
                "and exclusive offers."
            ),
            "priority": "High"
        }

    # --------------------------------------------------
    # Growth customers
    # --------------------------------------------------

    elif (
        income >= 35000
        and purchase_frequency >= 4
        and spend >= 2000
    ):
        persona = "Growth Customers"

        result = {
            "persona": persona,
            "description": (
                "Customers showing moderate purchasing activity "
                "with potential for higher engagement."
            ),
            "marketing_goal": (
                "Increase conversion and purchase frequency"
            ),
            "recommended_strategy": (
                "Use personalized offers, product recommendations "
                "and limited-time promotions."
            ),
            "recommended_content": (
                "Problem-solution content, product benefits "
                "and moderate promotional offers."
            ),
            "priority": "Medium"
        }

    # --------------------------------------------------
    # Emerging customers
    # --------------------------------------------------

    else:
        persona = "Emerging Customers"

        result = {
            "persona": persona,
            "description": (
                "Customers with lower spending and relatively "
                "lower purchase frequency or engagement."
            ),
            "marketing_goal": "Awareness and conversion",
            "recommended_strategy": (
                "Use introductory offers, educational content "
                "and low-risk incentives."
            ),
            "recommended_content": (
                "Short-form engaging content, introductory offers "
                "and clear calls to action."
            ),
            "priority": "Medium"
        }

    # --------------------------------------------------
    # Add characteristics
    # --------------------------------------------------

    profile = get_persona_profile(persona)

    result["characteristics"] = profile["characteristics"]
    result["marketing_needs"] = profile["marketing_needs"]
    result["preferred_approach"] = profile["preferred_approach"]

    return result


def interpret_segments(segment_summaries):
    """
    Add marketing interpretations to all segments.
    """

    interpreted_segments = []

    for segment in segment_summaries:

        interpretation = interpret_segment(
            segment
        )

        interpreted_segments.append({
            **segment,
            **interpretation
        })

    return interpreted_segments