"""
Rule-based agent for the StyleSenseEnv baseline.
Selects outfits based on simple logic: formality match + color harmony.
"""

import random
from typing import List, Dict
from env.models import Observation, OutfitAction, WardrobeItem, ClothingCategory, BuyItem


class RuleBasedAgent:
    """
    A simple rule-based agent to provide a non-trivial baseline.
    Logic:
    1. Filter wardrobe by category (top, bottom, shoes)
    2. Filter by formality range of the occasion
    3. Pick items that have some color harmony
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def act(self, obs: Observation) -> OutfitAction:
        """Select an outfit based on the observation."""
        wardrobe = obs.wardrobe
        occasion = obs.occasion
        
        # 1. Get formality range for occasion (approximate)
        # In a real scenario, the agent would use the provided occasion rules
        # Here we'll just try to match items with formality 5-8 for formal, 1-4 for casual
        is_formal = "formal" in occasion.value or "interview" in occasion.value or "meeting" in occasion.value or "wedding" in occasion.value
        f_min, f_max = (6, 10) if is_formal else (1, 5)

        # 2. Filter by category
        tops = [i for i in wardrobe if i.category == ClothingCategory.TOP]
        bottoms = [i for i in wardrobe if i.category == ClothingCategory.BOTTOM]
        shoes = [i for i in wardrobe if i.category == ClothingCategory.SHOES]
        outerwear = [i for i in wardrobe if i.category == ClothingCategory.OUTERWEAR]

        # 3. Filter by formality
        suitable_tops = [i for i in tops if f_min <= i.formality_level <= f_max] or tops
        suitable_bottoms = [i for i in bottoms if f_min <= i.formality_level <= f_max] or bottoms
        suitable_shoes = [i for i in shoes if f_min <= i.formality_level <= f_max] or shoes

        # 4. Pick a top and match colors
        top = self.rng.choice(suitable_tops)
        
        # Simple color matching: find a bottom with the same color or a neutral
        neutrals = {"black", "white", "grey", "navy", "beige"}
        matching_bottoms = [i for i in suitable_bottoms if i.color == top.color or i.color in neutrals] or suitable_bottoms
        bottom = self.rng.choice(matching_bottoms)
        
        matching_shoes = [i for i in suitable_shoes if i.color == bottom.color or i.color in neutrals] or suitable_shoes
        shoe = self.rng.choice(matching_shoes)

        # Optional outerwear for formal
        outer_id = None
        if is_formal and outerwear:
            suitable_outer = [i for i in outerwear if f_min <= i.formality_level <= f_max] or outerwear
            outer_id = self.rng.choice(suitable_outer).item_id

        return OutfitAction(
            top_item_id=top.item_id,
            bottom_item_id=bottom.item_id,
            shoes_item_id=shoe.item_id,
            outerwear_item_id=outer_id,
            color_palette_reasoning="Matching colors with neutrals for a cohesive look.",
            fit_reasoning="Selecting regular fits for comfort and occasion appropriateness.",
        )
