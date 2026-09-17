def generate_strategy(
    product,
    persona,
    marketing_goal,
    platform,
    budget,
    preferred_tone="Friendly"
):
    """
    Generate an explainable marketing strategy
    using customer intelligence and business inputs.
    """

    # --------------------------------------------------
    # Clean and normalize inputs
    # --------------------------------------------------

    goal = marketing_goal.strip().lower()
    platform_name = platform.strip().lower()
    persona_name = persona.strip()

    # --------------------------------------------------
    # 1. Base strategy from customer persona
    # --------------------------------------------------

    if persona_name == "High-Value Loyal Customers":

        base_strategy = {
            "campaign_type": "Retention and Upselling Campaign",
            "content_format": "Premium Social Post",
            "marketing_angle": "Loyalty, exclusivity and premium benefits",
            "cta": "Explore Your Exclusive Benefits",
            "offer": "VIP reward, loyalty benefit or premium upgrade",
            "kpis": [
                "Repeat Purchase Rate",
                "Average Order Value",
                "Conversion Rate"
            ]
        }

    elif persona_name == "Growth Customers":

        base_strategy = {
            "campaign_type": "Growth and Conversion Campaign",
            "content_format": "Promotional Post + Product Recommendation",
            "marketing_angle": "Product value + limited-time incentive",
            "cta": "Shop Now",
            "offer": "Limited-time discount or bundle offer",
            "kpis": [
                "Click-Through Rate",
                "Conversion Rate",
                "Purchase Frequency"
            ]
        }

    elif persona_name == "Emerging Customers":

        base_strategy = {
            "campaign_type": "Awareness and Acquisition Campaign",
            "content_format": "Short-form Social Content",
            "marketing_angle": "Simple benefits + low-risk introduction",
            "cta": "Try It Now",
            "offer": "Free trial, introductory discount or starter offer",
            "kpis": [
                "Reach",
                "Engagement Rate",
                "New Customer Conversion Rate"
            ]
        }

    else:

        # Fallback for unknown personas
        base_strategy = {
            "campaign_type": "General Marketing Campaign",
            "content_format": "Social Media Content",
            "marketing_angle": "Product value and customer benefits",
            "cta": "Learn More",
            "offer": "Introductory offer",
            "kpis": [
                "Reach",
                "Engagement Rate",
                "Conversion Rate"
            ]
        }

    # --------------------------------------------------
    # 2. Start with persona-based values
    # --------------------------------------------------

    campaign_type = base_strategy["campaign_type"]
    content_format = base_strategy["content_format"]
    marketing_angle = base_strategy["marketing_angle"]
    cta = base_strategy["cta"]
    offer = base_strategy["offer"]
    kpis = base_strategy["kpis"]

    # Always initialize the tone.
    recommended_tone = preferred_tone

    # --------------------------------------------------
    # 3. Marketing objective takes priority
    # --------------------------------------------------

    if goal == "awareness":

        campaign_type = "Brand Awareness Campaign"

        marketing_angle = (
            "Brand visibility, awareness and clear value proposition"
        )

        cta = "Discover More"

        kpis = [
            "Reach",
            "Impressions",
            "Engagement Rate"
        ]

        offer = (
            "Educational or value-focused introductory message"
        )

    elif goal == "engagement":

        campaign_type = "Audience Engagement Campaign"

        content_format = "Interactive Social Content"

        marketing_angle = (
            "Conversation, community and audience participation"
        )

        cta = "Share Your Opinion"

        kpis = [
            "Likes",
            "Comments",
            "Shares",
            "Engagement Rate"
        ]

        offer = (
            "Interactive question, poll, challenge or community activity"
        )

    elif goal == "conversion":

        campaign_type = "Conversion Campaign"

        marketing_angle = (
            "Clear product value + persuasive offer + strong CTA"
        )

        cta = "Buy Now"

        kpis = [
            "Click-Through Rate",
            "Conversion Rate",
            "Cost Per Conversion"
        ]

        # Customize offer according to persona
        if persona_name == "High-Value Loyal Customers":

            offer = (
                "Premium upgrade or exclusive loyalty offer"
            )

        elif persona_name == "Growth Customers":

            offer = (
                "Limited-time discount or bundle offer"
            )

        else:

            offer = (
                "Free trial, introductory discount or starter offer"
            )

    elif goal in ["retention", "customer retention"]:

        campaign_type = "Customer Retention Campaign"

        marketing_angle = (
            "Loyalty, repeat purchases and customer value"
        )

        cta = "Continue Your Journey"

        kpis = [
            "Repeat Purchase Rate",
            "Retention Rate",
            "Customer Lifetime Value"
        ]

        offer = (
            "Loyalty reward, personalized offer or exclusive benefit"
        )

    else:

        # Keep persona-based strategy if objective is not recognized
        campaign_type = base_strategy["campaign_type"]
        marketing_angle = base_strategy["marketing_angle"]
        cta = base_strategy["cta"]
        kpis = base_strategy["kpis"]
        offer = base_strategy["offer"]

    # --------------------------------------------------
    # 4. Platform-specific strategy
    # --------------------------------------------------

    if platform_name == "instagram":

        content_format = (
            f"{content_format} + Reel/Story variation"
        )

    elif platform_name == "linkedin":

        content_format = (
            "Professional post + thought-leadership variation"
        )

        recommended_tone = "Professional"

    elif platform_name == "facebook":

        content_format = (
            f"{content_format} + Community-focused variation"
        )

    elif platform_name == "email":

        content_format = (
            "Personalized email campaign"
        )

    elif platform_name in ["youtube", "youtube shorts"]:

        content_format = (
            "Short-form video campaign"
        )

    elif platform_name == "twitter" or platform_name == "x":

        content_format = (
            "Short-form text post + promotional variation"
        )

    # --------------------------------------------------
    # 5. Build explainable reasoning
    # --------------------------------------------------

    reasoning = (
        f"The strategy targets {persona_name} based on the "
        f"observed customer characteristics. The primary marketing "
        f"objective is {marketing_goal}, so the campaign is optimized "
        f"for that objective. The {platform} format is selected to "
        f"match the target audience and campaign goal. The recommended "
        f"tone is {recommended_tone}, while the selected CTA and offer "
        f"are intended to support the desired marketing outcome."
    )

    # --------------------------------------------------
    # 6. Return structured strategy
    # --------------------------------------------------

    return {
        "product": product,
        "target_persona": persona_name,
        "marketing_goal": marketing_goal,
        "platform": platform,
        "budget": budget,
        "campaign_type": campaign_type,
        "content_format": content_format,
        "marketing_angle": marketing_angle,
        "recommended_tone": recommended_tone,
        "call_to_action": cta,
        "recommended_offer": offer,
        "recommended_kpis": kpis,
        "reasoning": reasoning
    }