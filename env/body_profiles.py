"""
Body profile definitions and measurement-based body type classification.
"""

import random
from typing import Dict, List, Tuple
from env.models import BodyType, UserProfile


# ═══════════════════════════════════════════
#  BODY TYPE PROFILES
# ═══════════════════════════════════════════

BODY_TYPE_PROPORTIONS: Dict[BodyType, Dict] = {
    BodyType.PEAR: {
        "description": "Hips wider than shoulders, defined waist",
        "shoulder_hip_ratio": (0.70, 0.85),  # shoulder < hip
        "waist_hip_ratio": (0.65, 0.80),
        "typical_height_range": (155, 175),
    },
    BodyType.APPLE: {
        "description": "Broader midsection, shoulders and hips roughly equal",
        "shoulder_hip_ratio": (0.90, 1.10),
        "waist_hip_ratio": (0.85, 1.00),
        "typical_height_range": (155, 180),
    },
    BodyType.HOURGLASS: {
        "description": "Shoulders and hips roughly equal, defined waist",
        "shoulder_hip_ratio": (0.90, 1.10),
        "waist_hip_ratio": (0.60, 0.75),
        "typical_height_range": (155, 178),
    },
    BodyType.RECTANGLE: {
        "description": "Shoulders, waist, and hips roughly equal",
        "shoulder_hip_ratio": (0.90, 1.10),
        "waist_hip_ratio": (0.80, 0.95),
        "typical_height_range": (158, 185),
    },
    BodyType.INVERTED_TRIANGLE: {
        "description": "Shoulders wider than hips, athletic build",
        "shoulder_hip_ratio": (1.15, 1.40),
        "waist_hip_ratio": (0.70, 0.85),
        "typical_height_range": (160, 190),
    },
    BodyType.ATHLETIC: {
        "description": "Muscular build, defined shoulders, narrow waist",
        "shoulder_hip_ratio": (1.05, 1.30),
        "waist_hip_ratio": (0.65, 0.80),
        "typical_height_range": (160, 190),
    },
}

SKIN_TONES = [
    "warm_deep", "warm_medium", "warm_light",
    "cool_deep", "cool_medium", "cool_light",
    "neutral_deep", "neutral_medium", "neutral_light",
    "olive_medium", "olive_light",
]

AGE_GROUPS = ["teen", "young_adult", "adult", "senior"]
GENDER_PRESENTATIONS = ["masculine", "feminine", "androgynous"]

# Best colors by skin tone
SKIN_TONE_COLORS: Dict[str, Dict[str, List[str]]] = {
    "warm_deep": {
        "best": ["rust", "coral", "gold", "emerald", "warm_red", "terracotta"],
        "avoid": ["icy_blue", "silver", "pastel_pink"],
    },
    "warm_medium": {
        "best": ["olive", "peach", "warm_brown", "teal", "amber"],
        "avoid": ["cool_grey", "icy_lavender"],
    },
    "warm_light": {
        "best": ["peach", "coral", "warm_green", "camel", "ivory"],
        "avoid": ["black", "cool_navy"],
    },
    "cool_deep": {
        "best": ["royal_blue", "emerald", "magenta", "icy_pink", "pure_white"],
        "avoid": ["orange", "warm_yellow"],
    },
    "cool_medium": {
        "best": ["lavender", "rose", "navy", "burgundy", "cool_grey"],
        "avoid": ["orange", "rust", "warm_brown"],
    },
    "cool_light": {
        "best": ["soft_pink", "icy_blue", "lavender", "silver", "soft_white"],
        "avoid": ["orange", "gold", "warm_yellow"],
    },
    "neutral_deep": {
        "best": ["jade", "dusty_rose", "teal", "navy", "soft_white"],
        "avoid": [],
    },
    "neutral_medium": {
        "best": ["sage", "dusty_pink", "medium_blue", "soft_red"],
        "avoid": [],
    },
    "neutral_light": {
        "best": ["blush", "periwinkle", "soft_green", "light_grey"],
        "avoid": [],
    },
    "olive_medium": {
        "best": ["coral", "turquoise", "cream", "warm_red", "purple"],
        "avoid": ["yellow_green", "mustard"],
    },
    "olive_light": {
        "best": ["plum", "coral", "teal", "off_white", "dusty_rose"],
        "avoid": ["neon_yellow", "orange"],
    },
}


def generate_random_profile(rng: random.Random | None = None) -> UserProfile:
    """Generate a random but realistic user profile."""
    rng = rng or random.Random()

    body_type = rng.choice(list(BodyType))
    props = BODY_TYPE_PROPORTIONS[body_type]

    h_lo, h_hi = props["typical_height_range"]
    height = rng.uniform(h_lo, h_hi)

    # BMI-based weight estimation (18.5-30 BMI range)
    bmi = rng.uniform(18.5, 30.0)
    weight = bmi * (height / 100) ** 2

    # Generate proportional measurements
    hip = rng.uniform(85, 120)
    sh_lo, sh_hi = props["shoulder_hip_ratio"]
    shoulder = hip * rng.uniform(sh_lo, sh_hi)
    wh_lo, wh_hi = props["waist_hip_ratio"]
    waist = hip * rng.uniform(wh_lo, wh_hi)

    return UserProfile(
        body_type=body_type,
        height_cm=round(height, 1),
        weight_kg=round(weight, 1),
        shoulder_width_cm=round(shoulder / 2.5, 1),  # Convert circumference-ish to width
        waist_cm=round(waist, 1),
        hip_cm=round(hip, 1),
        skin_tone=rng.choice(SKIN_TONES),
        age_group=rng.choice(AGE_GROUPS),
        gender_presentation=rng.choice(GENDER_PRESENTATIONS),
    )


def classify_body_type(shoulder: float, waist: float, hip: float) -> BodyType:
    """Classify body type from measurements."""
    sh_ratio = shoulder / hip if hip > 0 else 1.0
    wh_ratio = waist / hip if hip > 0 else 1.0

    if sh_ratio < 0.85 and wh_ratio < 0.80:
        return BodyType.PEAR
    elif wh_ratio > 0.85 and 0.90 <= sh_ratio <= 1.10:
        return BodyType.APPLE
    elif 0.90 <= sh_ratio <= 1.10 and wh_ratio < 0.75:
        return BodyType.HOURGLASS
    elif 0.90 <= sh_ratio <= 1.10 and 0.80 <= wh_ratio <= 0.95:
        return BodyType.RECTANGLE
    elif sh_ratio > 1.15:
        return BodyType.INVERTED_TRIANGLE
    else:
        return BodyType.ATHLETIC
