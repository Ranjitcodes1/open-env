"""
Multi-objective reward function with 9 dimensions and penalties.
Provides partial progress signals — not just binary pass/fail.
Revised to include accessory variety and optimized lookups.
"""

from typing import List, Dict, Optional, Set
from env.models import (
    OutfitAction, Observation, RewardBreakdown,
    WardrobeItem, ClothingCategory,
)
from env.style_rules import score_outfit_color_harmony, score_body_flattery
from env.occasions import get_formality_range, is_sub_category_appropriate, is_color_appropriate
from env.cultural_context import score_cultural_compliance
from env.weather_sim import score_weather_appropriateness
from env.config import REWARD_WEIGHTS, PENALTIES


def resolve_items(
    action: OutfitAction, 
    wardrobe_map: Dict[str, WardrobeItem]
) -> tuple[List[WardrobeItem], List[str]]:
    """
    Resolve item IDs to actual WardrobeItem objects using a pre-built map.
    Returns (items, errors).
    """
    items = []
    errors = []

    # Required core items
    for field, item_id in [
        ("top", action.top_item_id),
        ("bottom", action.bottom_item_id),
        ("shoes", action.shoes_item_id),
    ]:
        if item_id in wardrobe_map:
            items.append(wardrobe_map[item_id])
        else:
            errors.append(f"Invalid {field} item_id: {item_id}")

    # Optional items
    if action.outerwear_item_id:
        if action.outerwear_item_id in wardrobe_map:
            items.append(wardrobe_map[action.outerwear_item_id])
        else:
            errors.append(f"Invalid outerwear item_id: {action.outerwear_item_id}")

    for acc_id in action.accessories:
        if acc_id in wardrobe_map:
            items.append(wardrobe_map[acc_id])
        else:
            errors.append(f"Invalid accessory item_id: {acc_id}")

    return items, errors


def _score_occasion(items: List[WardrobeItem], observation: Observation) -> float:
    """Score occasion appropriateness (0.0–1.0)."""
    min_f, max_f = get_formality_range(observation.occasion)
    score = 0.0
    checks = 0

    for item in items:
        if item.category in {ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.SHOES, ClothingCategory.OUTERWEAR}:
            checks += 1
            f = item.formality_level

            # Formality within range
            if min_f <= f <= max_f:
                score += 0.6
            elif abs(f - min_f) <= 1 or abs(f - max_f) <= 1:
                score += 0.3  # Close enough
            else:
                score += 0.0

            # Sub-category bonus/penalty
            result = is_sub_category_appropriate(item.sub_category, observation.occasion)
            if result is True:
                score += 0.3
            elif result is False:
                score -= 0.2
            else:
                score += 0.1  # Neutral

            # Color bonus/penalty
            color_result = is_color_appropriate(item.color, observation.occasion)
            if color_result is True:
                score += 0.1
            elif color_result is False:
                score -= 0.15

    return max(0.0, min(1.0, score / max(checks, 1)))


def _score_weather(items: List[WardrobeItem], observation: Observation) -> float:
    """Score weather suitability (0.0–1.0)."""
    scores = []
    for item in items:
        s = score_weather_appropriateness(
            item.weather_suitability,
            observation.weather,
            observation.season,
        )
        scores.append(s)
    return sum(scores) / len(scores) if scores else 0.5


def _score_budget(action: OutfitAction, budget_remaining: float) -> float:
    """Score budget efficiency (0.0–1.0)."""
    if not action.buy_new_items:
        return 1.0  # Used existing wardrobe

    total_cost = sum(item.max_price for item in action.buy_new_items)
    if total_cost > budget_remaining:
        return 0.0
    elif total_cost < budget_remaining * 0.5:
        return 0.9
    elif total_cost < budget_remaining * 0.8:
        return 0.7
    else:
        return 0.5


def _score_variety(action: OutfitAction, previous_outfits: List[Dict]) -> float:
    """
    Score outfit variety — penalize repetition (0.0–1.0).
    Now includes accessories in the uniqueness check.
    """
    if not previous_outfits:
        return 1.0

    current = {action.top_item_id, action.bottom_item_id, action.shoes_item_id}
    if action.outerwear_item_id:
        current.add(action.outerwear_item_id)
    if action.accessories:
        current.update(action.accessories)

    for prev in previous_outfits:
        prev_set = set(prev.get("item_ids", []))
        overlap = len(current & prev_set)
        if overlap == len(current):
            return 0.0  # Exact repeat
        elif overlap >= 3:
            return 0.3  # Significant overlap

    return 1.0


def _score_comfort(items: List[WardrobeItem], observation: Observation) -> float:
    """Score comfort based on weather, fit, and item condition (0.0–1.0)."""
    score = 0.5
    temp = observation.weather.temperature_c

    for item in items:
        if item.condition < 0.3:
            score -= 0.1
        if temp > 32 and item.fit in {"slim", "tailored"}:
            score -= 0.05
        if temp < 10 and item.fit in {"oversized", "relaxed"}:
            score += 0.05

    if observation.weather.is_rainy:
        shoe_items = [i for i in items if i.category == ClothingCategory.SHOES]
        for shoe in shoe_items:
            if shoe.sub_category in {"sandals", "flip_flops"}:
                score -= 0.2

    return max(0.0, min(1.0, score))


def compute_reward(
    action: OutfitAction,
    observation: Observation,
    previous_outfits: List[Dict],
    wardrobe_map: Dict[str, WardrobeItem],
    trend_scorer=None,
) -> RewardBreakdown:
    """
    Multi-objective reward with partial progress signals.
    9 dimensions, weighted sum, plus explicit penalties.
    """
    items, errors = resolve_items(action, wardrobe_map)
    penalties: Dict[str, float] = {}

    # Critical failure: invalid items
    if errors:
        penalties["invalid_items"] = PENALTIES["invalid_item"] * len(errors)
        return RewardBreakdown(
            total_reward=max(-1.0, sum(penalties.values())),
            penalties=penalties,
            feedback_message=f"Invalid items in outfit: {'; '.join(errors)}",
        )

    # Category validation
    categories_present = {i.category for i in items}
    required = {ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.SHOES}
    missing = required - categories_present
    if missing:
        penalties["missing_categories"] = PENALTIES["missing_category"] * len(missing)

    # ── Score each dimension ──
    occasion = _score_occasion(items, observation)
    body = score_body_flattery(items, observation.user_profile)
    
    outfit_colors = [i.color for i in items]
    color = score_outfit_color_harmony(outfit_colors)
    
    weather = _score_weather(items, observation)
    
    culture = score_cultural_compliance(
        item_sub_categories=[i.sub_category for i in items],
        item_colors=outfit_colors,
        item_fits=[i.fit.value for i in items],
        cultural_context=observation.cultural_context,
        occasion=observation.occasion,
    )

    if trend_scorer:
        outfit_patterns = [i.pattern.value for i in items]
        trend = trend_scorer.score_trend_alignment(outfit_colors, outfit_patterns)
    else:
        trend = 0.5

    budget = _score_budget(action, observation.budget_remaining)
    variety = _score_variety(action, previous_outfits)
    comfort = _score_comfort(items, observation)

    # ── Weighted total from config ──
    w = REWARD_WEIGHTS
    total = (
        w["occasion"] * occasion +
        w["body_flattery"] * body +
        w["color_harmony"] * color +
        w["weather"] * weather +
        w["culture"] * culture +
        w["trend"] * trend +
        w["budget"] * budget +
        w["variety"] * variety +
        w["comfort"] * comfort
    )

    # ── Penalties from config ──
    current_ids = {action.top_item_id, action.bottom_item_id, action.shoes_item_id}
    if action.outerwear_item_id: current_ids.add(action.outerwear_item_id)
    if action.accessories: current_ids.update(action.accessories)

    for prev in previous_outfits:
        if set(prev.get("item_ids", [])) == current_ids:
            penalties["exact_repetition"] = PENALTIES["exact_repetition"]
            break

    min_f, max_f = get_formality_range(observation.occasion)
    item_formalities = [i.formality_level for i in items if i.category != ClothingCategory.ACCESSORY]
    if item_formalities:
        avg_formality = sum(item_formalities) / len(item_formalities)
        if abs(avg_formality - (min_f + max_f) / 2) > 4:
            penalties["extreme_formality_mismatch"] = PENALTIES["extreme_formality_mismatch"]

    if action.buy_new_items:
        total_cost = sum(b.max_price for b in action.buy_new_items)
        if total_cost > observation.budget_remaining:
            penalties["budget_exceeded"] = PENALTIES["budget_exceeded"]

    total += sum(penalties.values())
    total = max(-1.0, min(1.0, round(total, 4)))

    # Feedback message construction (Improved clarity)
    feedback_parts = []
    if missing:
        feedback_parts.append(f"Missing core items: {[c.value for c in missing]}.")
    if occasion < 0.4:
        feedback_parts.append("Outfit doesn't suit the occasion well.")
    elif occasion >= 0.7:
        feedback_parts.append("Great occasion match!")
        
    if body >= 0.7: feedback_parts.append("Flattering for your body type.")
    if color >= 0.8: feedback_parts.append("Excellent color harmony!")
    if penalties:
        feedback_parts.append(f"Penalties: {', '.join(penalties.keys())}")

    return RewardBreakdown(
        occasion_appropriateness=round(occasion, 4),
        body_type_flattery=round(body, 4),
        color_harmony=round(color, 4),
        weather_suitability=round(weather, 4),
        cultural_compliance=round(culture, 4),
        trend_alignment=round(trend, 4),
        budget_efficiency=round(budget, 4),
        outfit_variety=round(variety, 4),
        comfort_score=round(comfort, 4),
        total_reward=total,
        penalties=penalties,
        feedback_message=" ".join(feedback_parts) if feedback_parts else "Outfit evaluated.",
    )
