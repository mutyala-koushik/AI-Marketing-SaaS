import re

from services.persona_profiles import get_persona_profile


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def normalize_text(text):
    if not text:
        return ""

    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


def count_matching_signals(text, signals):
    if not signals:
        return 0

    normalized = normalize_text(text)

    matches = 0

    for signal in signals:
        signal_normalized = normalize_text(signal)

        if signal_normalized in normalized:
            matches += 1

    return matches


def calculate_audience_relevance(
    content,
    persona
):
    profile = get_persona_profile(persona)

    signals = profile.get(
        "content_signals",
        []
    )

    if not signals:
        return 70

    matches = count_matching_signals(
        content,
        signals
    )

    if matches >= 5:
        return 95

    if matches == 4:
        return 90

    if matches == 3:
        return 85

    if matches == 2:
        return 78

    if matches == 1:
        return 70

    return 60


def calculate_goal_alignment(
    content,
    marketing_goal
):
    text = normalize_text(content)
    goal = normalize_text(marketing_goal)

    goal_signals = {
        "conversion": [
            "buy",
            "shop",
            "order",
            "start",
            "try",
            "offer",
            "discount",
            "trial",
            "today",
            "get started"
        ],

        "awareness": [
            "discover",
            "learn",
            "explore",
            "introducing",
            "experience",
            "new"
        ],

        "engagement": [
            "share",
            "comment",
            "opinion",
            "join",
            "tell us",
            "what do you think",
            "let us know"
        ],

        "retention": [
            "loyalty",
            "reward",
            "exclusive",
            "continue",
            "again",
            "benefit",
            "member"
        ]
    }

    signals = goal_signals.get(
        goal,
        []
    )

    if not signals:
        return 75

    matches = sum(
        signal in text
        for signal in signals
    )

    if matches >= 5:
        return 98

    if matches == 4:
        return 94

    if matches == 3:
        return 90

    if matches == 2:
        return 84

    if matches == 1:
        return 76

    return 62


def calculate_style_alignment(
    style,
    marketing_goal
):
    """
    Evaluate whether the campaign's creative style
    is appropriate for the marketing objective.
    """

    style_name = normalize_text(style)
    goal = normalize_text(marketing_goal)

    style_matrix = {
        "conversion": {
            "offer-focused": 98,
            "problem-solution": 94,
            "emotional": 88
        },

        "awareness": {
            "emotional": 98,
            "problem-solution": 90,
            "offer-focused": 82
        },

        "engagement": {
            "problem-solution": 96,
            "emotional": 94,
            "offer-focused": 82
        },

        "retention": {
            "emotional": 96,
            "offer-focused": 94,
            "problem-solution": 88
        }
    }

    goal_scores = style_matrix.get(
        goal,
        {}
    )

    return goal_scores.get(
        style_name,
        75
    )


def calculate_platform_fit(
    content,
    platform
):
    length = len(content)

    platform_name = normalize_text(
        platform
    )

    if platform_name == "instagram":

        if 80 <= length <= 500:
            return 95

        if length < 80:
            return 82

        if length <= 700:
            return 88

        return 72

    if platform_name == "linkedin":

        if 200 <= length <= 1500:
            return 95

        if length < 200:
            return 82

        return 80

    if platform_name == "facebook":

        if 100 <= length <= 1200:
            return 94

        return 82

    if platform_name == "email":

        if 200 <= length <= 2000:
            return 94

        return 80

    return 80


def calculate_cta_strength(
    content,
    call_to_action
):
    text = normalize_text(content)
    cta = normalize_text(call_to_action)

    if not cta:
        return 60

    if cta in text:
        return 98

    cta_words = [
        word
        for word in cta.split()
        if len(word) > 2
    ]

    if not cta_words:
        return 70

    matches = sum(
        word in text
        for word in cta_words
    )

    ratio = matches / len(cta_words)

    if ratio >= 0.75:
        return 88

    if ratio >= 0.50:
        return 78

    return 55


def calculate_offer_alignment(
    content,
    recommended_offer
):
    text = normalize_text(content)
    offer = normalize_text(
        recommended_offer
    )

    if not offer:
        return 70

    concepts = []

    if "free trial" in offer:
        concepts.extend([
            "free trial",
            "trial",
            "try",
            "start"
        ])

    if "discount" in offer:
        concepts.extend([
            "discount",
            "save",
            "offer"
        ])

    if "introductory" in offer:
        concepts.extend([
            "introductory",
            "starter",
            "begin",
            "start"
        ])

    if "loyalty" in offer:
        concepts.extend([
            "loyalty",
            "reward",
            "exclusive",
            "benefit"
        ])

    if not concepts:
        concepts = [
            word
            for word in offer.split()
            if len(word) > 3
        ]

    matches = sum(
        concept in text
        for concept in set(concepts)
    )

    if matches >= 4:
        return 98

    if matches == 3:
        return 93

    if matches == 2:
        return 87

    if matches == 1:
        return 78

    return 60


def calculate_readability(content):
    if not content.strip():
        return 0

    words = re.findall(
        r"\b[\w'-]+\b",
        content
    )

    if not words:
        return 0

    sentences = re.split(
        r"[.!?]+",
        content
    )

    sentences = [
        s.strip()
        for s in sentences
        if s.strip()
    ]

    if not sentences:
        return 60

    average_sentence_length = (
        len(words) / len(sentences)
    )

    long_words = sum(
        len(word) >= 14
        for word in words
    )

    repeated_words = 0

    normalized_words = [
        normalize_text(word)
        for word in words
    ]

    for index in range(
        1,
        len(normalized_words)
    ):
        if (
            normalized_words[index]
            == normalized_words[index - 1]
        ):
            repeated_words += 1

    score = 100

    if average_sentence_length > 30:
        score -= 20

    elif average_sentence_length > 24:
        score -= 12

    elif average_sentence_length > 20:
        score -= 6

    long_word_ratio = (
        long_words / len(words)
    )

    if long_word_ratio > 0.20:
        score -= 15

    elif long_word_ratio > 0.12:
        score -= 8

    if repeated_words >= 4:
        score -= 15

    elif repeated_words >= 2:
        score -= 8

    grammar_patterns = [
        r"\ba\s+easy\b",
        r"\ba\s+accessible\b",
        r"\ba\s+introductory\b",
        r"\ban\s+simple\b",
        r"\ba\s+offer\b",
        r"\ban\s+value\b"
    ]

    for pattern in grammar_patterns:
        if re.search(
            pattern,
            normalize_text(content)
        ):
            score -= 10

    if "!!" in content or "??" in content:
        score -= 5

    return clamp(
        round(score, 2)
    )


def calculate_factual_consistency(
    content,
    product,
    recommended_offer
):
    text = normalize_text(
        content
    )

    product_present = (
        normalize_text(product)
        in text
    )

    offer_present = any(
        concept in text
        for concept in [
            "free trial",
            "trial",
            "discount",
            "offer",
            "starter",
            "introductory",
            "loyalty",
            "reward"
        ]
    )

    if product_present and offer_present:
        return 96

    if product_present:
        return 88

    if offer_present:
        return 78

    return 65


def calculate_message_clarity(content):
    text = normalize_text(
        content
    )

    score = 100

    vague_phrases = [
        "something",
        "things",
        "stuff",
        "somehow",
        "maybe",
        "etc"
    ]

    vague_count = sum(
        phrase in text
        for phrase in vague_phrases
    )

    score -= vague_count * 7

    word_count = len(
        text.split()
    )

    if word_count > 150:
        score -= 10

    elif word_count > 100:
        score -= 5

    return clamp(score)


def evaluate_campaign_variant(
    variant,
    product,
    persona,
    marketing_goal,
    platform,
    call_to_action,
    recommended_offer
):
    content = variant.get(
        "content",
        ""
    )

    style = variant.get(
        "style",
        ""
    )

    audience_relevance = (
        calculate_audience_relevance(
            content,
            persona
        )
    )

    goal_alignment = (
        calculate_goal_alignment(
            content,
            marketing_goal
        )
    )

    style_alignment = (
        calculate_style_alignment(
            style,
            marketing_goal
        )
    )

    platform_fit = (
        calculate_platform_fit(
            content,
            platform
        )
    )

    cta_strength = (
        calculate_cta_strength(
            content,
            call_to_action
        )
    )

    offer_alignment = (
        calculate_offer_alignment(
            content,
            recommended_offer
        )
    )

    readability = (
        calculate_readability(
            content
        )
    )

    factual_consistency = (
        calculate_factual_consistency(
            content,
            product,
            recommended_offer
        )
    )

    message_clarity = (
        calculate_message_clarity(
            content
        )
    )

    overall = round(
        (
            audience_relevance * 0.20
            + goal_alignment * 0.20
            + style_alignment * 0.15
            + platform_fit * 0.10
            + cta_strength * 0.10
            + offer_alignment * 0.10
            + readability * 0.05
            + factual_consistency * 0.05
            + message_clarity * 0.05
        ),
        2
    )

    return {
        "variant_id": variant.get(
            "variant_id"
        ),
        "style": style,

        "scores": {
            "audience_relevance": audience_relevance,
            "goal_alignment": goal_alignment,
            "style_alignment": style_alignment,
            "platform_fit": platform_fit,
            "cta_strength": cta_strength,
            "offer_alignment": offer_alignment,
            "readability": readability,
            "factual_consistency": factual_consistency,
            "message_clarity": message_clarity,
            "overall": overall
        }
    }


def build_explanation(
    winner,
    evaluations
):
    scores = winner["scores"]

    dimensions = {
        "audience relevance":
            scores["audience_relevance"],

        "goal alignment":
            scores["goal_alignment"],

        "strategy/style alignment":
            scores["style_alignment"],

        "platform fit":
            scores["platform_fit"],

        "CTA strength":
            scores["cta_strength"],

        "offer alignment":
            scores["offer_alignment"],

        "readability":
            scores["readability"],

        "factual consistency":
            scores["factual_consistency"],

        "message clarity":
            scores["message_clarity"]
    }

    strongest = sorted(
        dimensions.items(),
        key=lambda item: item[1],
        reverse=True
    )[:3]

    strongest_text = ", ".join(
        f"{name} ({score}/100)"
        for name, score in strongest
    )

    runner_up = (
        evaluations[1]
        if len(evaluations) > 1
        else None
    )

    comparison = ""

    if runner_up:

        difference = round(
            winner["scores"]["overall"]
            - runner_up["scores"]["overall"],
            2
        )

        if difference > 0:
            comparison = (
                f" It ranked {difference} points "
                f"higher than the next variant."
            )

        else:
            comparison = (
                " It is tied with the next variant, "
                "so strategy/style alignment is used "
                "as the tie-breaker."
            )

    return (
        f"Variant {winner['variant_id']} "
        f"({winner['style']}) is recommended with "
        f"an overall score of "
        f"{scores['overall']}/100. "
        f"Its strongest areas are "
        f"{strongest_text}."
        f"{comparison}"
    )


def evaluate_campaign(
    variants,
    product,
    persona,
    characteristics,
    marketing_needs,
    marketing_goal,
    platform,
    call_to_action,
    recommended_offer
):
    evaluations = []

    for variant in variants:

        evaluation = evaluate_campaign_variant(
            variant=variant,
            product=product,
            persona=persona,
            marketing_goal=marketing_goal,
            platform=platform,
            call_to_action=call_to_action,
            recommended_offer=recommended_offer
        )

        evaluations.append(
            evaluation
        )

    # --------------------------------------------------
    # Primary ranking: overall score
    # Secondary ranking: style alignment
    # Tertiary ranking: goal alignment
    # --------------------------------------------------

    evaluations.sort(
        key=lambda item: (
            item["scores"]["overall"],
            item["scores"]["style_alignment"],
            item["scores"]["goal_alignment"]
        ),
        reverse=True
    )

    for rank, evaluation in enumerate(
        evaluations,
        start=1
    ):
        evaluation["rank"] = rank

    winner = evaluations[0]

    explanation = build_explanation(
        winner,
        evaluations
    )

    return {
        "evaluations": evaluations,
        "recommended_variant_id": (
            winner["variant_id"]
        ),
        "explanation": explanation
    }