"""
Cultural & regional styling norms and rules.
"""

from typing import Dict, List
from env.models import CulturalContext, Occasion


# ═══════════════════════════════════════════
#  CULTURAL STYLING RULES
# ═══════════════════════════════════════════

CULTURAL_RULES: Dict[CulturalContext, Dict] = {
    CulturalContext.WESTERN: {
        "formal_preferred": ["suit_jacket", "blazer", "dress_shirt", "dress_pants", "pencil_skirt", "heels", "oxford_shoes"],
        "casual_preferred": ["t_shirt", "jeans", "sneakers", "casual_shirt", "chinos"],
        "color_rules": {},  # Very flexible
        "modesty_level": "flexible",
        "special_occasions": {
            Occasion.WEDDING_GUEST: {"avoid_colors": ["white", "pure_white", "ivory"]},
            Occasion.FUNERAL: {"required_colors": ["black", "dark_grey", "navy"]},
        },
        "gender_neutral_acceptance": "high",
    },
    CulturalContext.INDO_WESTERN: {
        "formal_preferred": ["kurta", "blazer", "dress_shirt", "palazzo_pants", "ethnic_top"],
        "casual_preferred": ["kurta", "casual_shirt", "jeans", "chinos"],
        "color_rules": {
            "festive": ["bright_red", "gold", "saffron", "emerald", "royal_blue"],
            "avoid_festival": ["black", "dark_grey"],
        },
        "modesty_level": "moderate",
        "special_occasions": {
            Occasion.FESTIVAL: {"preferred_colors": ["bright_red", "gold", "saffron"], "preferred_items": ["kurta", "ethnic_top"]},
            Occasion.WEDDING_GUEST: {"preferred_items": ["kurta", "ethnic_top", "blazer"]},
        },
        "accessories": ["dupatta"],
        "gender_neutral_acceptance": "moderate",
    },
    CulturalContext.TRADITIONAL_INDIAN: {
        "formal_preferred": ["kurta", "ethnic_top"],
        "casual_preferred": ["kurta", "casual_shirt"],
        "color_rules": {
            "auspicious": ["red", "bright_red", "saffron", "gold"],
            "mourning": ["white", "pure_white"],
            "festive": ["bright_red", "gold", "saffron", "emerald", "royal_blue", "hot_pink"],
            "avoid_festival": ["black"],
        },
        "modesty_level": "high",
        "special_occasions": {
            Occasion.FESTIVAL: {
                "preferred_colors": ["bright_red", "gold", "saffron", "emerald"],
                "preferred_items": ["kurta", "ethnic_top"],
                "avoid_colors": ["black", "dark_grey"],
            },
            Occasion.WEDDING_GUEST: {
                "preferred_items": ["kurta", "ethnic_top"],
                "preferred_colors": ["bright_red", "gold", "royal_blue", "emerald"],
                "avoid_colors": ["white", "black"],
            },
            Occasion.FUNERAL: {
                "required_colors": ["white", "pure_white", "off_white"],
            },
        },
        "accessories": ["dupatta"],
        "gender_neutral_acceptance": "low",
    },
    CulturalContext.EAST_ASIAN: {
        "formal_preferred": ["blazer", "dress_shirt", "dress_pants", "pencil_skirt"],
        "casual_preferred": ["t_shirt", "casual_shirt", "jeans", "chinos"],
        "color_rules": {
            "lucky": ["red", "bright_red", "gold"],
            "mourning": ["white", "black"],
        },
        "modesty_level": "moderate",
        "special_occasions": {
            Occasion.FESTIVAL: {"preferred_colors": ["bright_red", "gold"]},
        },
        "gender_neutral_acceptance": "moderate",
    },
    CulturalContext.MIDDLE_EASTERN: {
        "formal_preferred": ["kurta", "blazer", "dress_shirt", "dress_pants"],
        "casual_preferred": ["casual_shirt", "chinos", "kurta"],
        "color_rules": {
            "preferred": ["earth_tones", "jewel_tones", "white"],
        },
        "modesty_level": "very_high",
        "preferred_fits": ["relaxed", "oversized", "regular"],
        "avoid_fits": ["slim"],
        "special_occasions": {},
        "gender_neutral_acceptance": "low",
    },
    CulturalContext.AFRICAN: {
        "formal_preferred": ["blazer", "dress_shirt", "dress_pants", "ethnic_top"],
        "casual_preferred": ["t_shirt", "casual_shirt", "jeans"],
        "color_rules": {
            "preferred": ["bright_colors", "earth_tones"],
            "patterns": ["geometric", "abstract"],
        },
        "modesty_level": "moderate",
        "special_occasions": {
            Occasion.FESTIVAL: {"preferred_patterns": ["geometric", "abstract"]},
        },
        "gender_neutral_acceptance": "moderate",
    },
}


def get_cultural_modesty_level(context: CulturalContext) -> str:
    """Get modesty level for a cultural context."""
    return CULTURAL_RULES[context]["modesty_level"]


def get_occasion_cultural_prefs(context: CulturalContext, occasion: Occasion) -> Dict:
    """Get cultural-specific preferences for an occasion."""
    rules = CULTURAL_RULES[context]
    return rules.get("special_occasions", {}).get(occasion, {})


def score_cultural_compliance(
    item_sub_categories: List[str],
    item_colors: List[str],
    item_fits: List[str],
    cultural_context: CulturalContext,
    occasion: Occasion,
) -> float:
    """
    Score how well an outfit complies with cultural norms (0.0–1.0).
    """
    rules = CULTURAL_RULES[cultural_context]
    score = 0.5  # Base neutral score

    # Modesty check
    modesty = rules["modesty_level"]
    high_exposure_items = {"crop_top", "tank_top", "shorts", "sleeveless"}
    exposed_count = sum(1 for sc in item_sub_categories if sc in high_exposure_items)

    if modesty == "very_high" and exposed_count > 0:
        score -= 0.3 * exposed_count
    elif modesty == "high" and exposed_count > 0:
        score -= 0.2 * exposed_count
    elif modesty == "moderate" and exposed_count > 1:
        score -= 0.1

    # Fit check for cultures that prefer relaxed fits
    avoid_fits = rules.get("avoid_fits", [])
    for fit in item_fits:
        if fit in avoid_fits:
            score -= 0.1

    preferred_fits = rules.get("preferred_fits", [])
    for fit in item_fits:
        if fit in preferred_fits:
            score += 0.05

    # Occasion-specific cultural rules
    occasion_prefs = get_occasion_cultural_prefs(cultural_context, occasion)
    if occasion_prefs:
        # Preferred colors
        pref_colors = occasion_prefs.get("preferred_colors", [])
        if pref_colors:
            matching = sum(1 for c in item_colors if c in pref_colors)
            if matching > 0:
                score += 0.15 * min(matching, 2)

        # Avoid colors
        avoid_colors = occasion_prefs.get("avoid_colors", [])
        for c in item_colors:
            if c in avoid_colors:
                score -= 0.2

        # Required colors
        req_colors = occasion_prefs.get("required_colors", [])
        if req_colors:
            has_required = any(c in req_colors for c in item_colors)
            if has_required:
                score += 0.2
            else:
                score -= 0.2

        # Preferred items
        pref_items = occasion_prefs.get("preferred_items", [])
        if pref_items:
            matching_items = sum(1 for sc in item_sub_categories if sc in pref_items)
            score += 0.1 * min(matching_items, 2)

    return max(0.0, min(1.0, score))
