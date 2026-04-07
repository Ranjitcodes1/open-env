"""
Weather and season simulation.
"""

import random
from typing import Dict, List
from env.models import Season, WeatherCondition


# ═══════════════════════════════════════════
#  SEASON → WEATHER RANGES
# ═══════════════════════════════════════════

SEASON_WEATHER: Dict[Season, Dict] = {
    Season.SUMMER: {
        "temp_range": (28, 42),
        "humidity_range": (30, 70),
        "rain_probability": 0.1,
        "wind_range": (5, 20),
        "uv_range": (6, 11),
    },
    Season.WINTER: {
        "temp_range": (-5, 18),
        "humidity_range": (30, 60),
        "rain_probability": 0.15,
        "wind_range": (10, 40),
        "uv_range": (1, 4),
    },
    Season.MONSOON: {
        "temp_range": (22, 34),
        "humidity_range": (70, 95),
        "rain_probability": 0.7,
        "wind_range": (10, 45),
        "uv_range": (2, 6),
    },
    Season.SPRING: {
        "temp_range": (18, 30),
        "humidity_range": (35, 60),
        "rain_probability": 0.2,
        "wind_range": (5, 25),
        "uv_range": (4, 8),
    },
    Season.AUTUMN: {
        "temp_range": (12, 25),
        "humidity_range": (35, 65),
        "rain_probability": 0.25,
        "wind_range": (8, 30),
        "uv_range": (3, 6),
    },
}


def generate_weather(season: Season, rng: random.Random | None = None) -> WeatherCondition:
    """Generate realistic weather for a given season."""
    rng = rng or random.Random()
    config = SEASON_WEATHER[season]

    t_lo, t_hi = config["temp_range"]
    h_lo, h_hi = config["humidity_range"]
    w_lo, w_hi = config["wind_range"]
    u_lo, u_hi = config["uv_range"]

    return WeatherCondition(
        temperature_c=round(rng.uniform(t_lo, t_hi), 1),
        humidity_percent=round(rng.uniform(h_lo, h_hi), 1),
        is_rainy=rng.random() < config["rain_probability"],
        wind_speed_kmh=round(rng.uniform(w_lo, w_hi), 1),
        uv_index=round(rng.uniform(u_lo, u_hi), 1),
    )


def vary_weather(base: WeatherCondition, rng: random.Random | None = None) -> WeatherCondition:
    """Create a slight variation of existing weather (for day-to-day changes in hard task)."""
    rng = rng or random.Random()
    return WeatherCondition(
        temperature_c=round(base.temperature_c + rng.uniform(-4, 4), 1),
        humidity_percent=round(max(0, min(100, base.humidity_percent + rng.uniform(-10, 10))), 1),
        is_rainy=rng.random() < (0.5 if base.is_rainy else 0.15),
        wind_speed_kmh=round(max(0, base.wind_speed_kmh + rng.uniform(-5, 5)), 1),
        uv_index=round(max(0, min(12, base.uv_index + rng.uniform(-2, 2))), 1),
    )


def score_weather_appropriateness(
    item_seasons: List[Season],
    weather: WeatherCondition,
    current_season: Season,
) -> float:
    """
    Score how weather-appropriate a clothing item is (0.0–1.0).
    """
    score = 0.5

    # Season match
    if current_season in item_seasons:
        score += 0.3
    else:
        score -= 0.2

    # Temperature-specific checks
    temp = weather.temperature_c
    if temp > 35:
        # Very hot — penalize heavy items
        if Season.WINTER in item_seasons and Season.SUMMER not in item_seasons:
            score -= 0.3
        if Season.SUMMER in item_seasons:
            score += 0.1
    elif temp < 10:
        # Cold — penalize light items
        if Season.SUMMER in item_seasons and Season.WINTER not in item_seasons:
            score -= 0.3
        if Season.WINTER in item_seasons:
            score += 0.1

    # Rain check — open shoes are bad in rain
    if weather.is_rainy:
        # We can't check shoe type here directly, but seasonal match helps
        if Season.MONSOON in item_seasons:
            score += 0.1

    return max(0.0, min(1.0, score))
