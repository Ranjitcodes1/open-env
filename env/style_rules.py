"""
Fashion rule engine — body type flattery, color theory, and fit rules.
"""

from typing import Dict, List, Set, Tuple
from env.models import BodyType, FitType, WardrobeItem, UserProfile, ClothingCategory


# ═══════════════════════════════════════════
#  BODY TYPE → FLATTERING STYLE RULES
# ═══════════════════════════════════════════

BODY_STYLE_RULES: Dict[BodyType, Dict] = {
    BodyType.PEAR: {
        "flattering_tops": ["blouse", "nice_blouse", "dress_shirt", "casual_shirt", "polo_shirt"],
        "flattering_bottoms": ["a_line_skirt", "wide_leg_pants", "palazzo_pants", "straight_leg_pants"],
        "avoid_bottoms": ["leggings", "pencil_skirt"],
        "best_fits_top": [FitType.TAILORED, FitType.REGULAR],
        "best_fits_bottom": [FitType.RELAXED, FitType.REGULAR],
        "avoid_fits_bottom": [FitType.SLIM],
        "detail_advice": "Draw attention upward with structured shoulders and bright tops, darker bottoms",
        "top_color_strategy": "bright",
        "bottom_color_strategy": "dark",
    },
    BodyType.APPLE: {
        "flattering_tops": ["blouse", "nice_blouse", "casual_shirt", "kurta"],
        "flattering_bottoms": ["straight_leg_pants", "wide_leg_pants", "jeans"],
        "avoid_tops": ["crop_top", "tank_top"],
        "best_fits_top": [FitType.RELAXED, FitType.REGULAR],
        "best_fits_bottom": [FitType.REGULAR, FitType.RELAXED],
        "avoid_fits_top": [FitType.SLIM],
        "detail_advice": "V-necklines and longline layers elongate the torso",
        "top_color_strategy": "solid_dark",
        "bottom_color_strategy": "any",
    },
    BodyType.HOURGLASS: {
        "flattering_tops": ["blouse", "nice_blouse", "dress_shirt", "sweater"],
        "flattering_bottoms": ["pencil_skirt", "fitted_jeans", "dress_pants", "a_line_skirt"],
        "best_fits_top": [FitType.TAILORED, FitType.SLIM],
        "best_fits_bottom": [FitType.TAILORED, FitType.SLIM],
        "avoid_fits_any": [FitType.OVERSIZED],
        "detail_advice": "Highlight the waist with belted styles, fitted cuts",
        "top_color_strategy": "any",
        "bottom_color_strategy": "any",
    },
    BodyType.RECTANGLE: {
        "flattering_tops": ["blouse", "nice_blouse", "casual_shirt", "sweater", "polo_shirt"],
        "flattering_bottoms": ["a_line_skirt", "wide_leg_pants", "chinos", "jeans"],
        "best_fits_top": [FitType.REGULAR, FitType.TAILORED],
        "best_fits_bottom": [FitType.REGULAR, FitType.RELAXED],
        "detail_advice": "Create curves with peplum tops, belted waists, and layered outfits",
        "top_color_strategy": "any",
        "bottom_color_strategy": "any",
    },
    BodyType.INVERTED_TRIANGLE: {
        "flattering_tops": ["casual_shirt", "sweater", "t_shirt"],
        "flattering_bottoms": ["wide_leg_pants", "a_line_skirt", "palazzo_pants", "fitted_jeans"],
        "avoid_tops": ["blazer", "suit_jacket"],  # Adds more shoulder width
        "best_fits_top": [FitType.REGULAR, FitType.RELAXED],
        "best_fits_bottom": [FitType.REGULAR, FitType.RELAXED],
        "avoid_fits_top": [FitType.TAILORED],  # Emphasizes broad shoulders
        "detail_advice": "Balance broad shoulders with volume on the bottom half",
        "top_color_strategy": "dark",
        "bottom_color_strategy": "bright",
    },
    BodyType.ATHLETIC: {
        "flattering_tops": ["blouse", "nice_blouse", "casual_shirt", "dress_shirt", "polo_shirt"],
        "flattering_bottoms": ["chinos", "fitted_jeans", "dress_pants", "a_line_skirt"],
        "best_fits_top": [FitType.TAILORED, FitType.SLIM],
        "best_fits_bottom": [FitType.TAILORED, FitType.SLIM],
        "detail_advice": "Structured, fitted clothing highlights a toned physique",
        "top_color_strategy": "any",
        "bottom_color_strategy": "any",
    },
}


# ═══════════════════════════════════════════
#  COLOR THEORY RULES
# ═══════════════════════════════════════════

# Groups of colors that harmonize well together
COLOR_GROUPS = {
    "neutrals": {"black", "white", "grey", "light_grey", "charcoal", "beige", "cream", "ivory", "off_white", "pure_white"},
    "warm_earths": {"khaki", "camel", "tan", "warm_brown", "chocolate", "espresso", "rust", "terracotta"},
    "cool_blues": {"navy", "royal_blue", "light_blue", "sky_blue", "teal"},
    "greens": {"emerald", "forest_green", "sage", "olive", "mint"},
    "warm_reds": {"burgundy", "deep_red", "coral"},
    "purples": {"lavender", "purple", "plum", "mauve"},
    "pinks": {"hot_pink", "dusty_pink", "blush", "soft_pink"},
    "golds": {"gold", "saffron", "mustard", "amber"},
}

# Classic complementary combinations
COMPLEMENTARY_PAIRS: List[Tuple[str, str]] = [
    ("navy", "rust"), ("navy", "cream"), ("navy", "white"),
    ("charcoal", "burgundy"), ("charcoal", "light_blue"),
    ("black", "white"), ("black", "deep_red"),
    ("emerald", "burgundy"), ("forest_green", "coral"),
    ("teal", "coral"), ("teal", "gold"),
    ("olive", "cream"), ("olive", "burgundy"),
    ("royal_blue", "gold"), ("royal_blue", "white"),
    ("lavender", "sage"), ("lavender", "cream"),
    ("plum", "gold"), ("plum", "cream"),
    ("camel", "navy"), ("camel", "white"),
    ("beige", "navy"), ("beige", "burgundy"),
    ("grey", "dusty_pink"), ("grey", "light_blue"),
]

# Colors that clash
CLASHING_PAIRS: List[Tuple[str, str]] = [
    ("hot_pink", "deep_red"), ("hot_pink", "orange"),
    ("royal_blue", "purple"), ("rust", "hot_pink"),
    ("emerald", "teal"),
    ("mustard", "gold"),
]


def _get_color_group(color: str) -> str | None:
    """Find which color group a color belongs to."""
    for group_name, colors in COLOR_GROUPS.items():
        if color in colors:
            return group_name
    return None


def score_color_pair(color1: str, color2: str) -> float:
    """
    Score how well two colors work together (0.0-1.0).
    """
    if color1 == color2:
        return 0.7  # Monochromatic is safe but not exciting

    # Check for complementary pairs
    if (color1, color2) in COMPLEMENTARY_PAIRS or (color2, color1) in COMPLEMENTARY_PAIRS:
        return 1.0

    # Check for clashing pairs
    if (color1, color2) in CLASHING_PAIRS or (color2, color1) in CLASHING_PAIRS:
        return 0.1

    # Neutrals go with everything
    neutrals = COLOR_GROUPS["neutrals"]
    if color1 in neutrals or color2 in neutrals:
        return 0.85

    # Same color group = analogous (pretty good)
    g1, g2 = _get_color_group(color1), _get_color_group(color2)
    if g1 and g2 and g1 == g2:
        return 0.75

    # Different groups, not complementary = mediocre
    return 0.5


def score_outfit_color_harmony(colors: List[str]) -> float:
    """Score overall color harmony of an outfit (0.0-1.0)."""
    if not colors or len(colors) < 2:
        return 0.5

    scores = []
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            scores.append(score_color_pair(colors[i], colors[j]))

    return sum(scores) / len(scores) if scores else 0.5


def score_body_flattery(items: List[WardrobeItem], profile: UserProfile) -> float:
    """
    Score how well the outfit items flatter the user's body type (0.0-1.0).
    """
    rules = BODY_STYLE_RULES.get(profile.body_type, {})
    if not rules:
        return 0.5

    score = 0.0
    checks = 0

    for item in items:
        # Check flattering sub-categories
        if item.category == ClothingCategory.TOP:
            flattering = rules.get("flattering_tops", [])
            avoid = rules.get("avoid_tops", [])
            best_fits = rules.get("best_fits_top", [])
            avoid_fits = rules.get("avoid_fits_top", [])
        elif item.category == ClothingCategory.BOTTOM:
            flattering = rules.get("flattering_bottoms", [])
            avoid = rules.get("avoid_bottoms", [])
            best_fits = rules.get("best_fits_bottom", [])
            avoid_fits = rules.get("avoid_fits_bottom", [])
        else:
            continue

        checks += 1

        # Sub-category scoring
        if item.sub_category in flattering:
            score += 0.5
        elif item.sub_category in avoid:
            score += 0.0
        else:
            score += 0.3  # Neutral

        # Fit scoring
        if item.fit in best_fits:
            score += 0.5
        elif item.fit in avoid_fits:
            score += 0.05
        elif item.fit in rules.get("avoid_fits_any", []):
            score += 0.05
        else:
            score += 0.3

    return min(1.0, score / max(checks, 1))
