"""
Wardrobe item database and random wardrobe generator.
"""

import random
from typing import List, Dict
from env.models import (
    WardrobeItem, ClothingCategory, FitType, PatternType, Season,
)
from env.config import ITEM_ID_PREFIX


# ═══════════════════════════════════════════
#  CLOTHING ITEM TEMPLATES
# ═══════════════════════════════════════════

ITEM_TEMPLATES: Dict[str, Dict] = {
    # ── TOPS ──
    "t_shirt": {
        "category": ClothingCategory.TOP,
        "formality_range": (1, 3),
        "fits": [FitType.SLIM, FitType.REGULAR, FitType.OVERSIZED],
        "seasons": [[Season.SUMMER, Season.SPRING], [Season.SUMMER], [Season.SPRING, Season.AUTUMN]],
        "price_range": (10, 40),
    },
    "dress_shirt": {
        "category": ClothingCategory.TOP,
        "formality_range": (6, 9),
        "fits": [FitType.SLIM, FitType.REGULAR, FitType.TAILORED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER, Season.SUMMER]],
        "price_range": (30, 80),
    },
    "casual_shirt": {
        "category": ClothingCategory.TOP,
        "formality_range": (3, 6),
        "fits": [FitType.REGULAR, FitType.RELAXED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.SUMMER]],
        "price_range": (25, 60),
    },
    "blouse": {
        "category": ClothingCategory.TOP,
        "formality_range": (5, 8),
        "fits": [FitType.REGULAR, FitType.TAILORED, FitType.RELAXED],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (30, 75),
    },
    "nice_blouse": {
        "category": ClothingCategory.TOP,
        "formality_range": (6, 8),
        "fits": [FitType.TAILORED, FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (40, 90),
    },
    "tank_top": {
        "category": ClothingCategory.TOP,
        "formality_range": (1, 2),
        "fits": [FitType.SLIM, FitType.REGULAR],
        "seasons": [[Season.SUMMER]],
        "price_range": (8, 25),
    },
    "polo_shirt": {
        "category": ClothingCategory.TOP,
        "formality_range": (3, 5),
        "fits": [FitType.SLIM, FitType.REGULAR],
        "seasons": [[Season.SUMMER, Season.SPRING]],
        "price_range": (25, 55),
    },
    "hoodie": {
        "category": ClothingCategory.TOP,
        "formality_range": (1, 3),
        "fits": [FitType.REGULAR, FitType.OVERSIZED],
        "seasons": [[Season.AUTUMN, Season.WINTER, Season.SPRING]],
        "price_range": (30, 70),
    },
    "sweater": {
        "category": ClothingCategory.TOP,
        "formality_range": (3, 6),
        "fits": [FitType.REGULAR, FitType.RELAXED, FitType.SLIM],
        "seasons": [[Season.AUTUMN, Season.WINTER]],
        "price_range": (35, 80),
    },
    "kurta": {
        "category": ClothingCategory.TOP,
        "formality_range": (4, 8),
        "fits": [FitType.REGULAR, FitType.RELAXED],
        "seasons": [[Season.SUMMER, Season.SPRING, Season.AUTUMN, Season.MONSOON]],
        "price_range": (30, 100),
        "cultural_tags": ["traditional_indian", "indo_western"],
    },
    "ethnic_top": {
        "category": ClothingCategory.TOP,
        "formality_range": (4, 7),
        "fits": [FitType.REGULAR, FitType.TAILORED],
        "seasons": [[Season.SUMMER, Season.SPRING, Season.AUTUMN]],
        "price_range": (25, 70),
        "cultural_tags": ["traditional_indian", "indo_western"],
    },
    "crop_top": {
        "category": ClothingCategory.TOP,
        "formality_range": (1, 3),
        "fits": [FitType.SLIM, FitType.REGULAR],
        "seasons": [[Season.SUMMER, Season.SPRING]],
        "price_range": (15, 35),
    },
    "sports_bra": {
        "category": ClothingCategory.TOP,
        "formality_range": (1, 1),
        "fits": [FitType.SLIM],
        "seasons": [[Season.SUMMER, Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (20, 50),
    },

    # ── BOTTOMS ──
    "jeans": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (2, 5),
        "fits": [FitType.SLIM, FitType.REGULAR, FitType.RELAXED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (30, 80),
    },
    "fitted_jeans": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (3, 5),
        "fits": [FitType.SLIM, FitType.TAILORED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (40, 90),
    },
    "dress_pants": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (7, 9),
        "fits": [FitType.TAILORED, FitType.SLIM, FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER, Season.SUMMER]],
        "price_range": (40, 100),
    },
    "chinos": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (4, 6),
        "fits": [FitType.SLIM, FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (30, 70),
    },
    "shorts": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (1, 3),
        "fits": [FitType.REGULAR, FitType.RELAXED],
        "seasons": [[Season.SUMMER]],
        "price_range": (15, 45),
    },
    "track_pants": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (1, 2),
        "fits": [FitType.REGULAR, FitType.RELAXED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER, Season.SUMMER]],
        "price_range": (20, 50),
    },
    "a_line_skirt": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (4, 7),
        "fits": [FitType.REGULAR, FitType.TAILORED],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (25, 65),
    },
    "pencil_skirt": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (6, 9),
        "fits": [FitType.SLIM, FitType.TAILORED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (35, 80),
    },
    "wide_leg_pants": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (4, 7),
        "fits": [FitType.RELAXED, FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (35, 75),
    },
    "palazzo_pants": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (4, 7),
        "fits": [FitType.RELAXED],
        "seasons": [[Season.SUMMER, Season.SPRING, Season.MONSOON]],
        "price_range": (30, 65),
        "cultural_tags": ["indo_western"],
    },
    "leggings": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (1, 3),
        "fits": [FitType.SLIM],
        "seasons": [[Season.AUTUMN, Season.WINTER, Season.SPRING]],
        "price_range": (15, 40),
    },
    "straight_leg_pants": {
        "category": ClothingCategory.BOTTOM,
        "formality_range": (5, 7),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (35, 75),
    },

    # ── OUTERWEAR ──
    "blazer": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (7, 9),
        "fits": [FitType.TAILORED, FitType.SLIM],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (60, 150),
    },
    "casual_blazer": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (5, 7),
        "fits": [FitType.REGULAR, FitType.RELAXED],
        "seasons": [[Season.SPRING, Season.AUTUMN]],
        "price_range": (50, 120),
    },
    "suit_jacket": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (8, 10),
        "fits": [FitType.TAILORED],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (100, 250),
    },
    "denim_jacket": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (2, 4),
        "fits": [FitType.REGULAR, FitType.OVERSIZED],
        "seasons": [[Season.SPRING, Season.AUTUMN]],
        "price_range": (40, 90),
    },
    "leather_jacket": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (3, 6),
        "fits": [FitType.SLIM, FitType.REGULAR],
        "seasons": [[Season.AUTUMN, Season.WINTER]],
        "price_range": (80, 200),
    },
    "puffer_jacket": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (2, 4),
        "fits": [FitType.REGULAR, FitType.OVERSIZED],
        "seasons": [[Season.WINTER]],
        "price_range": (60, 150),
    },
    "cardigan": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (3, 6),
        "fits": [FitType.REGULAR, FitType.RELAXED, FitType.OVERSIZED],
        "seasons": [[Season.AUTUMN, Season.WINTER, Season.SPRING]],
        "price_range": (30, 70),
    },
    "longline_blazer": {
        "category": ClothingCategory.OUTERWEAR,
        "formality_range": (6, 9),
        "fits": [FitType.TAILORED, FitType.REGULAR],
        "seasons": [[Season.AUTUMN, Season.WINTER, Season.SPRING]],
        "price_range": (70, 160),
    },

    # ── SHOES ──
    "sneakers": {
        "category": ClothingCategory.SHOES,
        "formality_range": (1, 4),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (40, 120),
    },
    "running_shoes": {
        "category": ClothingCategory.SHOES,
        "formality_range": (1, 2),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]],
        "price_range": (50, 150),
    },
    "oxford_shoes": {
        "category": ClothingCategory.SHOES,
        "formality_range": (7, 10),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (60, 180),
    },
    "loafers": {
        "category": ClothingCategory.SHOES,
        "formality_range": (5, 8),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (50, 130),
    },
    "heels": {
        "category": ClothingCategory.SHOES,
        "formality_range": (6, 10),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (40, 150),
    },
    "pumps": {
        "category": ClothingCategory.SHOES,
        "formality_range": (7, 10),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN]],
        "price_range": (50, 160),
    },
    "chelsea_boots": {
        "category": ClothingCategory.SHOES,
        "formality_range": (4, 7),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.AUTUMN, Season.WINTER]],
        "price_range": (60, 150),
    },
    "sandals": {
        "category": ClothingCategory.SHOES,
        "formality_range": (1, 4),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SUMMER]],
        "price_range": (15, 50),
    },
    "flip_flops": {
        "category": ClothingCategory.SHOES,
        "formality_range": (1, 1),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SUMMER]],
        "price_range": (5, 20),
    },
    "boots": {
        "category": ClothingCategory.SHOES,
        "formality_range": (3, 6),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.AUTUMN, Season.WINTER, Season.MONSOON]],
        "price_range": (50, 140),
    },

    # ── ACCESSORIES ──
    "watch": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (3, 10),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]],
        "price_range": (30, 200),
    },
    "belt": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (3, 9),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]],
        "price_range": (15, 60),
    },
    "scarf": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (3, 7),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.AUTUMN, Season.WINTER]],
        "price_range": (15, 50),
    },
    "sunglasses": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (2, 6),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SUMMER, Season.SPRING]],
        "price_range": (10, 100),
    },
    "necklace": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (3, 9),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]],
        "price_range": (10, 80),
    },
    "earrings": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (3, 9),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]],
        "price_range": (8, 60),
    },
    "tie": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (7, 10),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.AUTUMN, Season.WINTER]],
        "price_range": (20, 60),
    },
    "handbag": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (3, 8),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]],
        "price_range": (30, 150),
    },
    "dupatta": {
        "category": ClothingCategory.ACCESSORY,
        "formality_range": (4, 8),
        "fits": [FitType.REGULAR],
        "seasons": [[Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.MONSOON]],
        "price_range": (15, 60),
        "cultural_tags": ["traditional_indian", "indo_western"],
    },
}

# Common colors for clothing items
CLOTHING_COLORS = [
    "black", "white", "navy", "charcoal", "grey", "light_grey",
    "beige", "cream", "ivory", "khaki", "camel", "tan",
    "burgundy", "deep_red", "coral", "rust", "terracotta",
    "royal_blue", "light_blue", "teal", "sky_blue",
    "emerald", "forest_green", "sage", "olive", "mint",
    "lavender", "purple", "plum", "mauve",
    "hot_pink", "dusty_pink", "blush", "soft_pink",
    "gold", "saffron", "mustard", "amber",
    "warm_brown", "chocolate", "espresso",
    "off_white", "pure_white",
]


def generate_wardrobe(
    size: int = 30,
    rng: random.Random | None = None,
    cultural_bias: str | None = None,
) -> List[WardrobeItem]:
    """
    Generate a random wardrobe with a balanced mix of categories.
    
    Args:
        size: Number of items (20-50)
        rng: Random number generator for reproducibility
        cultural_bias: If set, includes more items with that cultural tag
    """
    rng = rng or random.Random()
    items: List[WardrobeItem] = []

    # Ensure minimum coverage: at least 6 tops, 5 bottoms, 2 outerwear, 4 shoes, 3 accessories
    category_targets = {
        ClothingCategory.TOP: max(6, int(size * 0.25)),
        ClothingCategory.BOTTOM: max(5, int(size * 0.20)),
        ClothingCategory.OUTERWEAR: max(2, int(size * 0.12)),
        ClothingCategory.SHOES: max(4, int(size * 0.18)),
        ClothingCategory.ACCESSORY: max(3, int(size * 0.15)),
    }

    # Adjust to match total size
    total_target = sum(category_targets.values())
    if total_target < size:
        category_targets[ClothingCategory.TOP] += size - total_target

    templates_by_category: Dict[ClothingCategory, List[str]] = {}
    for name, tmpl in ITEM_TEMPLATES.items():
        cat = tmpl["category"]
        if cat not in templates_by_category:
            templates_by_category[cat] = []
        templates_by_category[cat].append(name)

    item_counter = 0
    for category, count in category_targets.items():
        available = templates_by_category.get(category, [])
        if not available:
            continue

        for _ in range(count):
            sub_cat = rng.choice(available)
            tmpl = ITEM_TEMPLATES[sub_cat]

            f_lo, f_hi = tmpl["formality_range"]
            formality = rng.randint(f_lo, f_hi)
            fit = rng.choice(tmpl["fits"])
            seasons = rng.choice(tmpl["seasons"])
            p_lo, p_hi = tmpl["price_range"]
            price = round(rng.uniform(p_lo, p_hi), 2)
            color = rng.choice(CLOTHING_COLORS)
            pattern = rng.choice(list(PatternType))
            cultural_tags = list(tmpl.get("cultural_tags", []))

            # Additive cultural bias
            if cultural_bias and cultural_bias not in cultural_tags and rng.random() < 0.2:
                cultural_tags.append(cultural_bias)

            items.append(WardrobeItem(
                item_id=f"{ITEM_ID_PREFIX}{item_counter:03d}",
                category=category,
                sub_category=sub_cat,
                color=color,
                pattern=pattern,
                fit=fit,
                formality_level=formality,
                weather_suitability=seasons,
                cultural_tags=cultural_tags,
                price=price,
                condition=round(rng.uniform(0.5, 1.0), 2),
            ))
            item_counter += 1

    rng.shuffle(items)
    return items


def get_items_by_category(
    wardrobe: List[WardrobeItem], category: ClothingCategory
) -> List[WardrobeItem]:
    """Filter wardrobe items by category."""
    return [item for item in wardrobe if item.category == category]
