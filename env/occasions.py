"""
Occasion types, dress code rules, and formality mappings.
"""

from typing import Dict, List, Optional
from env.models import Occasion


# ═══════════════════════════════════════════
#  OCCASION FORMALITY RULES
# ═══════════════════════════════════════════

OCCASION_RULES: Dict[Occasion, Dict] = {
    Occasion.JOB_INTERVIEW: {
        "min_formality": 7,
        "max_formality": 9,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["blazer", "dress_shirt", "dress_pants", "pencil_skirt", "oxford_shoes", "pumps"],
        "forbidden_sub_categories": ["tank_top", "flip_flops", "shorts", "sneakers", "crop_top"],
        "preferred_colors": ["navy", "charcoal", "black", "white", "light_blue"],
        "forbidden_colors": ["neon_green", "neon_pink", "hot_pink"],
        "notes": "Professional, conservative, well-fitted",
    },
    Occasion.CASUAL_OUTING: {
        "min_formality": 2,
        "max_formality": 5,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["t_shirt", "jeans", "sneakers", "casual_shirt", "chinos", "sundress"],
        "forbidden_sub_categories": ["tuxedo", "ball_gown"],
        "preferred_colors": [],  # Any works
        "forbidden_colors": [],
        "notes": "Relaxed, comfortable, personal expression",
    },
    Occasion.FORMAL_DINNER: {
        "min_formality": 8,
        "max_formality": 10,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["suit_jacket", "dress_shirt", "dress_pants", "evening_dress", "heels", "oxford_shoes"],
        "forbidden_sub_categories": ["t_shirt", "sneakers", "shorts", "flip_flops"],
        "preferred_colors": ["black", "navy", "burgundy", "emerald", "gold"],
        "forbidden_colors": ["neon_green", "neon_orange"],
        "notes": "Elegant, sophisticated, polished",
    },
    Occasion.WEDDING_GUEST: {
        "min_formality": 7,
        "max_formality": 10,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["dress", "suit", "saree", "lehenga", "sherwani"],
        "forbidden_sub_categories": ["t_shirt", "sneakers", "shorts"],
        "preferred_colors": ["pastel_pink", "lavender", "teal", "gold", "emerald"],
        "forbidden_colors": ["white", "pure_white", "ivory"],  # Don't upstage bride
        "notes": "Festive but not white — never upstage the bride/groom",
    },
    Occasion.GYM_WORKOUT: {
        "min_formality": 1,
        "max_formality": 2,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["tank_top", "sports_bra", "track_pants", "shorts", "running_shoes", "sneakers"],
        "forbidden_sub_categories": ["blazer", "heels", "dress_shirt", "suit_jacket"],
        "preferred_colors": [],
        "forbidden_colors": [],
        "notes": "Functional, breathable, performance-oriented",
    },
    Occasion.DATE_NIGHT: {
        "min_formality": 5,
        "max_formality": 8,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["nice_blouse", "fitted_jeans", "dress", "casual_blazer", "chelsea_boots", "heels"],
        "forbidden_sub_categories": ["track_pants", "flip_flops", "tank_top"],
        "preferred_colors": ["burgundy", "black", "deep_red", "emerald", "warm_tones"],
        "forbidden_colors": [],
        "notes": "Attractive, confident, slightly elevated casual",
    },
    Occasion.BUSINESS_MEETING: {
        "min_formality": 6,
        "max_formality": 9,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["blazer", "dress_shirt", "dress_pants", "pencil_skirt", "loafers", "oxford_shoes"],
        "forbidden_sub_categories": ["shorts", "flip_flops", "tank_top", "crop_top"],
        "preferred_colors": ["navy", "charcoal", "grey", "white", "light_blue"],
        "forbidden_colors": ["neon_green", "hot_pink"],
        "notes": "Authoritative, trustworthy, polished",
    },
    Occasion.COLLEGE_CLASS: {
        "min_formality": 2,
        "max_formality": 5,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["t_shirt", "jeans", "sneakers", "hoodie", "casual_shirt", "chinos"],
        "forbidden_sub_categories": ["tuxedo", "ball_gown", "heels"],
        "preferred_colors": [],
        "forbidden_colors": [],
        "notes": "Comfortable, practical, youthful",
    },
    Occasion.FESTIVAL: {
        "min_formality": 3,
        "max_formality": 8,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["kurta", "saree", "lehenga", "sherwani", "dress", "ethnic_top"],
        "forbidden_sub_categories": [],
        "preferred_colors": ["bright_red", "gold", "royal_blue", "emerald", "hot_pink", "saffron"],
        "forbidden_colors": ["black", "dark_grey"],  # Festivals are vibrant
        "notes": "Vibrant, festive, culturally expressive",
    },
    Occasion.FUNERAL: {
        "min_formality": 7,
        "max_formality": 9,
        "required_categories": ["top", "bottom", "shoes"],
        "preferred_sub_categories": ["suit", "dress_shirt", "dress_pants", "modest_dress", "oxford_shoes"],
        "forbidden_sub_categories": ["shorts", "tank_top", "crop_top", "flip_flops"],
        "preferred_colors": ["black", "dark_grey", "navy", "dark_brown"],
        "forbidden_colors": ["bright_red", "hot_pink", "neon_green", "gold", "bright_yellow"],
        "notes": "Somber, respectful, conservative",
    },
}


def get_formality_range(occasion: Occasion) -> tuple[int, int]:
    """Return (min_formality, max_formality) for an occasion."""
    rules = OCCASION_RULES[occasion]
    return rules["min_formality"], rules["max_formality"]


def is_sub_category_appropriate(sub_category: str, occasion: Occasion) -> Optional[bool]:
    """
    Check if a sub-category is appropriate for the occasion.
    Returns True (preferred), False (forbidden), or None (neutral).
    """
    rules = OCCASION_RULES[occasion]
    if sub_category in rules.get("forbidden_sub_categories", []):
        return False
    if sub_category in rules.get("preferred_sub_categories", []):
        return True
    return None


def is_color_appropriate(color: str, occasion: Occasion) -> Optional[bool]:
    """
    Check if a color is appropriate for the occasion.
    Returns True (preferred), False (forbidden), or None (neutral).
    """
    rules = OCCASION_RULES[occasion]
    if color in rules.get("forbidden_colors", []):
        return False
    if rules.get("preferred_colors") and color in rules["preferred_colors"]:
        return True
    return None
