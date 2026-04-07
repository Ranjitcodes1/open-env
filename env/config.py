"""
Centralized configuration weights and thresholds for StyleSenseEnv.
"""

# ═══════════════════════════════════════════
#  REWARD WEIGHTS (Sum should be 1.0)
# ═══════════════════════════════════════════

REWARD_WEIGHTS = {
    "occasion": 0.20,
    "body_flattery": 0.20,
    "color_harmony": 0.15,
    "weather": 0.10,
    "culture": 0.10,
    "trend": 0.08,
    "budget": 0.07,
    "variety": 0.05,
    "comfort": 0.05,
}

# ═══════════════════════════════════════════
#  GRADER THRESHOLDS (Passing Scores)
# ═══════════════════════════════════════════

PASSING_THRESHOLDS = {
    "easy": 0.6,
    "medium": 0.5,
    "hard": 0.4,
}

# ═══════════════════════════════════════════
#  PENALTIES
# ═══════════════════════════════════════════

PENALTIES = {
    "invalid_item": -0.5,
    "missing_category": -0.3,
    "exact_repetition": -0.3,
    "extreme_formality_mismatch": -0.4,
    "budget_exceeded": -0.3,
}

# ═══════════════════════════════════════════
#  ENVIRONMENT CONSTANTS
# ═══════════════════════════════════════════

DEFAULT_SEED = 42
MAX_ACCESSORIES = 3
ITEM_ID_PREFIX = "item_"
BOUGHT_ITEM_PREFIX = "bought_"
