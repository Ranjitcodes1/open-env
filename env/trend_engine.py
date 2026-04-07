"""
Dynamic fashion trend simulation — non-stationary trend shifts.
"""

import random
from typing import Dict, List
from env.models import TrendState


# ═══════════════════════════════════════════
#  TREND CYCLES
# ═══════════════════════════════════════════

TREND_CYCLES: Dict[int, Dict[str, List[str]]] = {
    1: {
        "colors": ["sage", "lavender", "cream", "soft_pink", "sky_blue"],
        "styles": ["minimalist", "quiet_luxury", "clean_lines"],
        "patterns": ["solid", "subtle_texture", "monochrome"],
    },
    2: {
        "colors": ["hot_pink", "royal_blue", "coral", "emerald", "gold"],
        "styles": ["bold", "maximalist", "color_blocking"],
        "patterns": ["abstract", "color_block", "geometric"],
    },
    3: {
        "colors": ["rust", "terracotta", "olive", "warm_brown", "mustard"],
        "styles": ["vintage", "bohemian", "earthy"],
        "patterns": ["floral", "paisley", "checked"],
    },
    4: {
        "colors": ["burgundy", "emerald", "gold", "plum", "deep_red"],
        "styles": ["elegant", "festive", "glamorous"],
        "patterns": ["velvet", "sequin", "rich_texture"],
    },
}


class TrendEngine:
    """
    Simulates shifting fashion trends across quarters.
    Non-stationary: the agent must adapt as trends change.
    """

    def __init__(self, initial_quarter: int | None = None, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.quarter = initial_quarter or self.rng.randint(1, 4)
        self._micro_shift_count = 0

    def get_current_trends(self) -> TrendState:
        """Get the current trend snapshot."""
        cycle = TREND_CYCLES[self.quarter]
        return TrendState(
            trending_colors=cycle["colors"],
            trending_styles=cycle["styles"],
            trending_patterns=cycle["patterns"],
            trend_quarter=self.quarter,
        )

    def advance_quarter(self):
        """Move to the next quarter (used in hard task)."""
        self.quarter = (self.quarter % 4) + 1
        self._micro_shift_count = 0

    def micro_shift(self):
        """
        Small mid-quarter trend shift (used in hard task within a week).
        Swaps 1-2 trending items to simulate organic change.
        """
        self._micro_shift_count += 1
        cycle = TREND_CYCLES[self.quarter]

        # Every 3 micro-shifts, swap one trending color with a random one
        if self._micro_shift_count % 3 == 0:
            all_colors = []
            for q in TREND_CYCLES.values():
                all_colors.extend(q["colors"])
            all_colors = list(set(all_colors))

            idx = self.rng.randint(0, len(cycle["colors"]) - 1)
            new_color = self.rng.choice(all_colors)
            cycle["colors"][idx] = new_color

    def score_trend_alignment(self, outfit_colors: List[str], outfit_patterns: List[str]) -> float:
        """
        Score how well an outfit aligns with current trends (0.0–1.0).
        """
        trends = self.get_current_trends()
        score = 0.0
        checks = 0

        # Color alignment
        for color in outfit_colors:
            checks += 1
            if color in trends.trending_colors:
                score += 1.0
            else:
                # Partial credit for colors in same family
                score += 0.3

        # Pattern alignment
        for pattern in outfit_patterns:
            checks += 1
            if pattern in trends.trending_patterns:
                score += 1.0
            else:
                score += 0.3

        return min(1.0, score / max(checks, 1))

    def reset(self, quarter: int | None = None):
        """Reset to a specific or random quarter."""
        self.quarter = quarter or self.rng.randint(1, 4)
        self._micro_shift_count = 0
