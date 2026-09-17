PERSONA_PROFILES = {
    "High-Value Loyal Customers": {
        "characteristics": [
            "high spending",
            "frequent purchases",
            "strong digital engagement",
            "high purchase activity",
            "strong interest in the product"
        ],

        "marketing_needs": [
            "premium value",
            "exclusive benefits",
            "loyalty recognition",
            "personalized experiences"
        ],

        "preferred_approach": (
            "Focus on loyalty, premium value, exclusivity "
            "and personalized benefits."
        ),

        # Customer-facing concepts the evaluator should look for.
        "content_signals": [
            "premium",
            "exclusive",
            "loyalty",
            "reward",
            "vip",
            "personalized",
            "benefits",
            "upgrade",
            "special"
        ]
    },

    "Growth Customers": {
        "characteristics": [
            "moderate spending",
            "moderate purchase frequency",
            "moderate digital engagement",
            "existing interest in the product",
            "potential for increased purchase activity"
        ],

        "marketing_needs": [
            "stronger product value",
            "reasons to purchase more frequently",
            "relevant recommendations",
            "limited-time incentives"
        ],

        "preferred_approach": (
            "Focus on product value, relevant recommendations "
            "and incentives that encourage higher purchase activity."
        ),

        "content_signals": [
            "value",
            "benefit",
            "save",
            "offer",
            "discount",
            "bundle",
            "recommendation",
            "upgrade",
            "more",
            "limited-time"
        ]
    },

    "Emerging Customers": {
        "characteristics": [
            "younger customer profile",
            "lower average spending",
            "lower purchase frequency",
            "lower digital engagement",
            "potential to develop into regular customers"
        ],

        "marketing_needs": [
            "simple value proposition",
            "low-risk introduction",
            "easy-to-understand benefits",
            "strong reason to try the product"
        ],

        "preferred_approach": (
            "Focus on simple benefits, accessibility, "
            "low-risk offers and clear calls to action."
        ),

        "content_signals": [
            "simple",
            "easy",
            "accessible",
            "affordable",
            "starter",
            "begin",
            "start",
            "try",
            "trial",
            "introductory",
            "routine",
            "habit",
            "convenient",
            "low-pressure",
            "easy-to-use"
        ]
    }
}


def get_persona_profile(persona):
    """
    Return the marketing profile associated with
    an internally generated customer persona.
    """

    return PERSONA_PROFILES.get(
        persona,
        {
            "characteristics": [
                "general customer profile"
            ],

            "marketing_needs": [
                "clear product value"
            ],

            "preferred_approach": (
                "Focus on clear product benefits and relevance."
            ),

            "content_signals": [
                "simple",
                "benefit",
                "value",
                "useful",
                "easy"
            ]
        }
    )