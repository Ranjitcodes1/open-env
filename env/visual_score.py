"""
Visual harmony and proportion scoring.
Evaluates outfit cohesion from a visual perspective.
"""

from typing import List, Dict
from env.models import WardrobeItem, UserProfile, FitType, ClothingCategory


def score_visual_proportion(items: List[WardrobeItem], profile: UserProfile) -> float:
    """
    Score how visually balanced the outfit proportions are (0.0–1.0).
    Considers fit combinations and how they interact with body proportions.
    """
    tops = [i for i in items if i.category == ClothingCategory.TOP]
    bottoms = [i for i in items if i.category == ClothingCategory.BOTTOM]
    outerwear = [i for i in items if i.category == ClothingCategory.OUTERWEAR]

    score = 0.5  # Base

    # Rule: avoid all-oversized (shapeless) or all-slim (too tight)
    all_fits = [i.fit for i in items if i.category in {ClothingCategory.TOP, ClothingCategory.BOTTOM}]
    if all_fits:
        if all(f == FitType.OVERSIZED for f in all_fits):
            score -= 0.2  # All loose = shapeless
        elif all(f == FitType.SLIM for f in all_fits):
            score -= 0.1  # All tight = uncomfortable looking

    # Balanced silhouette: one fitted + one relaxed = good
    fit_set = set(all_fits)
    if (FitType.SLIM in fit_set or FitType.TAILORED in fit_set) and \
       (FitType.RELAXED in fit_set or FitType.REGULAR in fit_set):
        score += 0.2  # Balanced

    # Outerwear adds structure (bonus if present for formal occasions)
    if outerwear:
        score += 0.1

    # Layering bonus: top + outerwear = polished
    if tops and outerwear:
        top_formality = max(t.formality_level for t in tops)
        outer_formality = max(o.formality_level for o in outerwear)
        if abs(top_formality - outer_formality) <= 2:
            score += 0.1  # Formality-consistent layers

    # Height-aware proportion hints
    if profile.height_cm < 160:
        # Shorter frame: high-waisted + slim bottoms elongate
        for b in bottoms:
            if b.fit in [FitType.SLIM, FitType.TAILORED]:
                score += 0.05
    elif profile.height_cm > 180:
        # Taller frame: can carry oversized/relaxed fits
        for item in tops:
            if item.fit == FitType.OVERSIZED:
                score += 0.05

    return max(0.0, min(1.0, score))


def score_formality_consistency(items: List[WardrobeItem]) -> float:
    """
    Score how consistent the formality level is across outfit pieces (0.0–1.0).
    A blazer with flip-flops scores poorly.
    """
    formality_levels = [i.formality_level for i in items]
    if not formality_levels:
        return 0.5

    avg = sum(formality_levels) / len(formality_levels)
    max_deviation = max(abs(f - avg) for f in formality_levels)

    # Low deviation = consistent = good
    if max_deviation <= 1:
        return 1.0
    elif max_deviation <= 2:
        return 0.8
    elif max_deviation <= 3:
        return 0.6
    elif max_deviation <= 4:
        return 0.3
    else:
        return 0.1  # Blazer + flip-flops territory


def score_pattern_mixing(items: List[WardrobeItem]) -> float:
    """
    Score pattern mixing (0.0–1.0).
    1 pattern + solids = great. 2+ bold patterns = risky.
    """
    from env.models import PatternType

    patterns = [i.pattern for i in items if i.category in {ClothingCategory.TOP, ClothingCategory.BOTTOM, ClothingCategory.OUTERWEAR}]
    if not patterns:
        return 0.5

    non_solid = [p for p in patterns if p != PatternType.SOLID]
    solid_count = patterns.count(PatternType.SOLID)

    if len(non_solid) == 0:
        return 0.7  # All solid is safe
    elif len(non_solid) == 1 and solid_count >= 1:
        return 1.0  # One pattern + solids = perfect
    elif len(non_solid) == 2:
        # Two patterns: OK if they're different scales (abstracted as different types)
        if non_solid[0] != non_solid[1]:
            return 0.5  # Different patterns, risky but can work
        else:
            return 0.3  # Same pattern twice = bad
    else:
        return 0.2  # Pattern overload


def score_overall_visual(items: List[WardrobeItem], profile: UserProfile) -> float:
    """Combined visual score."""
    proportion = score_visual_proportion(items, profile)
    formality = score_formality_consistency(items)
    pattern = score_pattern_mixing(items)

    return round(0.4 * proportion + 0.35 * formality + 0.25 * pattern, 4)
