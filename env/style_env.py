"""
StyleSenseEnv: OpenEnv-compliant environment for fashion recommendations.
Handles core physics/logic for wardrobe matching and reward calculation.
"""

import random
from typing import Dict, List, Optional, Any
from env.models import (
    Observation, OutfitAction, RewardBreakdown,
    UserProfile, WeatherCondition, WardrobeItem,
    ScheduleEvent, Season, Occasion, CulturalContext,
)
from env.body_profiles import generate_random_profile
from env.wardrobe import generate_wardrobe, ITEM_TEMPLATES, CLOTHING_COLORS
from env.weather_sim import generate_weather, vary_weather
from env.trend_engine import TrendEngine
from env.reward import compute_reward
from env.config import DEFAULT_SEED


# --- Task Setup ---

TASK_CONFIGS = {
    "easy": {
        "name": "Single Outfit Recommendation",
        "description": "Recommend one appropriate outfit for a given body type and occasion",
        "difficulty": "easy",
        "max_steps": 1,
        "wardrobe_size": 25,
        "budget": 0,
        "schedule_events": 1,
        "trend_shifts": False,
        "weather_changes": False,
    },
    "medium": {
        "name": "Full-Day Multi-Occasion Styling",
        "description": "Plan outfits for 3-4 events in a single day using a shared wardrobe",
        "difficulty": "medium",
        "max_steps": 4,
        "wardrobe_size": 35,
        "budget": 100,
        "schedule_events": 4,
        "trend_shifts": False,
        "weather_changes": False,
    },
    "hard": {
        "name": "Weekly Wardrobe Optimization",
        "description": "Style a full week with budget constraints, changing weather, and trend shifts",
        "difficulty": "hard",
        "max_steps": 21,
        "wardrobe_size": 45,
        "budget": 500,
        "schedule_events": 21,
        "trend_shifts": True,
        "weather_changes": True,
    },
}

# Day schedules for medium task
MEDIUM_SCHEDULES = [
    [
        ScheduleEvent(time="09:00", occasion=Occasion.BUSINESS_MEETING, duration_hours=3, location="office"),
        ScheduleEvent(time="12:30", occasion=Occasion.CASUAL_OUTING, duration_hours=1.5, location="restaurant"),
        ScheduleEvent(time="17:00", occasion=Occasion.GYM_WORKOUT, duration_hours=1.5, location="gym"),
        ScheduleEvent(time="20:00", occasion=Occasion.DATE_NIGHT, duration_hours=2.5, location="restaurant"),
    ],
    [
        ScheduleEvent(time="08:30", occasion=Occasion.JOB_INTERVIEW, duration_hours=2, location="office"),
        ScheduleEvent(time="11:00", occasion=Occasion.COLLEGE_CLASS, duration_hours=3, location="university"),
        ScheduleEvent(time="15:00", occasion=Occasion.CASUAL_OUTING, duration_hours=2, location="mall"),
        ScheduleEvent(time="19:00", occasion=Occasion.FORMAL_DINNER, duration_hours=3, location="restaurant"),
    ],
]


def _build_hard_schedule(rng: random.Random) -> List[ScheduleEvent]:
    """Get 7-day schedule for the week-long task."""
    schedule = []
    time_slots = [("09:00", 3.0, "morning"), ("14:00", 3.0, "afternoon"), ("19:00", 3.0, "evening")]

    for day in range(7):
        for time_str, duration, period in time_slots:
            if period == "morning":
                pool = [Occasion.BUSINESS_MEETING, Occasion.JOB_INTERVIEW, Occasion.COLLEGE_CLASS, Occasion.CASUAL_OUTING]
            elif period == "afternoon":
                pool = [Occasion.CASUAL_OUTING, Occasion.COLLEGE_CLASS, Occasion.GYM_WORKOUT, Occasion.BUSINESS_MEETING]
            else:
                pool = [Occasion.DATE_NIGHT, Occasion.FORMAL_DINNER, Occasion.CASUAL_OUTING, Occasion.FESTIVAL, Occasion.WEDDING_GUEST]

            schedule.append(ScheduleEvent(
                time=f"D{day+1}_{time_str}",
                occasion=rng.choice(pool),
                duration_hours=duration,
                location=rng.choice(["indoor", "outdoor"]),
            ))
    return schedule


class StyleSenseEnv:
    """Core environment implementation."""

    def __init__(self, seed: int | None = DEFAULT_SEED):
        self.rng = random.Random(seed)
        self.seed = seed
        self.trend_engine = TrendEngine(rng=self.rng)

        # State variables
        self._task_id: str = "easy"
        self._task_config: Dict = TASK_CONFIGS["easy"]
        self._profile: Optional[UserProfile] = None
        self._wardrobe: List[WardrobeItem] = []
        self._wardrobe_map: Dict[str, WardrobeItem] = {}  # Cached lookups
        self._season: Season = Season.SUMMER
        self._weather: WeatherCondition = WeatherCondition(
            temperature_c=30, humidity_percent=50, is_rainy=False,
            wind_speed_kmh=10, uv_index=5,
        )
        self._cultural_context: CulturalContext = CulturalContext.WESTERN
        self._budget: float = 0
        self._schedule: List[ScheduleEvent] = []
        self._current_step: int = 0
        self._previous_outfits: List[Dict] = []
        self._cumulative_reward: float = 0.0
        self._done: bool = False
        self._episode_rewards: List[RewardBreakdown] = []
        self._used_items: set = set()

    def reset(self, task_id: str = "easy", seed: Optional[int] = None) -> Observation:
        """Reset for path-based or seed-based evaluation."""
        if seed is not None:
            self.rng = random.Random(seed)
            self.seed = seed

        if task_id not in TASK_CONFIGS:
            raise ValueError(f"Unknown task_id: {task_id}")

        self._task_id = task_id
        self._task_config = TASK_CONFIGS[task_id]
        self._profile = generate_random_profile(self.rng)
        self._season = self.rng.choice(list(Season))
        self._cultural_context = self.rng.choice(list(CulturalContext))
        self._weather = generate_weather(self._season, self.rng)

        cultural_bias = "traditional_indian" if self._cultural_context in {CulturalContext.TRADITIONAL_INDIAN, CulturalContext.INDO_WESTERN} else None
        self._wardrobe = generate_wardrobe(
            size=self._task_config["wardrobe_size"],
            rng=self.rng,
            cultural_bias=cultural_bias,
        )
        # Update wardrobe map for O(1) lookups
        self._wardrobe_map = {item.item_id: item for item in self._wardrobe}

        self._budget = float(self._task_config["budget"])

        if task_id == "easy":
            self._schedule = [ScheduleEvent(time="12:00", occasion=self.rng.choice(list(Occasion)))]
        elif task_id == "medium":
            self._schedule = self.rng.choice(MEDIUM_SCHEDULES).copy()
        elif task_id == "hard":
            self._schedule = _build_hard_schedule(self.rng)

        self.trend_engine.reset()
        self._current_step = 0
        self._previous_outfits = []
        self._cumulative_reward = 0.0
        self._done = False
        self._episode_rewards = []
        self._used_items = set()

        return self._build_observation()

    def step(self, action: OutfitAction) -> tuple[Observation, RewardBreakdown, bool, Dict]:
        """Execute one recommendation step."""
        if self._done:
            raise RuntimeError("Episode is done. Call reset().")
        if self._profile is None:
            raise RuntimeError("Call reset() first.")

        observation = self._build_observation()

        # Compute reward with cached map
        reward = compute_reward(
            action=action,
            observation=observation,
            previous_outfits=self._previous_outfits,
            wardrobe_map=self._wardrobe_map,
            trend_scorer=self.trend_engine,
        )

        # Process buy actions
        if action.buy_new_items:
            total_cost = sum(b.max_price for b in action.buy_new_items)
            if total_cost <= self._budget:
                self._budget -= total_cost
                for buy in action.buy_new_items:
                    template = ITEM_TEMPLATES.get(buy.sub_category)
                    if template:
                        new_item = WardrobeItem(
                            item_id=f"bought_{len(self._wardrobe):03d}",
                            category=buy.category,
                            sub_category=buy.sub_category,
                            color=buy.color if buy.color in CLOTHING_COLORS else self.rng.choice(CLOTHING_COLORS),
                            formality_level=self.rng.randint(*template["formality_range"]),
                            fit=self.rng.choice(template["fits"]),
                            weather_suitability=self.rng.choice(template["seasons"]),
                            price=buy.max_price,
                            condition=1.0,
                        )
                        self._wardrobe.append(new_item)
                        self._wardrobe_map[new_item.item_id] = new_item

        # Record outfit
        outfit_ids = [action.top_item_id, action.bottom_item_id, action.shoes_item_id]
        if action.outerwear_item_id: outfit_ids.append(action.outerwear_item_id)
        outfit_ids.extend(action.accessories)

        self._previous_outfits.append({
            "item_ids": outfit_ids,
            "step": self._current_step,
            "reward": reward.total_reward,
        })
        self._episode_rewards.append(reward)
        self._cumulative_reward += reward.total_reward
        self._used_items.update(outfit_ids)

        # Advance step
        self._current_step += 1

        # Hard task dynamics
        if self._task_id == "hard":
            if self._task_config["weather_changes"] and self._current_step % 3 == 0:
                self._weather = vary_weather(self._weather, self.rng)
            if self._task_config["trend_shifts"] and self._current_step % 7 == 0:
                self.trend_engine.micro_shift()

        self._done = self._current_step >= self._task_config["max_steps"]
        
        info = {
            "step": self._current_step,
            "cumulative_reward": round(self._cumulative_reward, 4),
            "done": self._done,
            "budget_remaining": round(self._budget, 2),
        }

        return self._build_observation(), reward, self._done, info

    def state(self) -> Dict:
        """Return current environment state snapshot."""
        return {
            "task_id": self._task_id,
            "profile": self._profile.model_dump() if self._profile else None,
            "budget_remaining": round(self._budget, 2),
            "current_step": self._current_step,
            "done": self._done,
            "cumulative_reward": round(self._cumulative_reward, 4),
            "current_trends": self.trend_engine.get_current_trends().model_dump(),
        }

    def _build_observation(self) -> Observation:
        """Build the current observation."""
        current_event_idx = min(self._current_step, len(self._schedule) - 1)
        current_event = self._schedule[current_event_idx] if self._schedule else None

        return Observation(
            user_profile=self._profile,
            occasion=current_event.occasion if current_event else Occasion.CASUAL_OUTING,
            season=self._season,
            weather=self._weather,
            cultural_context=self._cultural_context,
            current_trends=self.trend_engine.get_current_trends(),
            wardrobe=self._wardrobe,
            budget_remaining=round(self._budget, 2),
            day_schedule=[e.model_dump() for e in self._schedule],
            episode_step=self._current_step,
            max_steps=self._task_config["max_steps"],
            previous_outfits=self._previous_outfits,
            current_event_index=current_event_idx,
        )

    def get_episode_summary(self) -> Dict:
        """Summary for grading."""
        return {
            "task_id": self._task_id,
            "total_steps": self._current_step,
            "cumulative_reward": round(self._cumulative_reward, 4),
            "average_reward": round(self._cumulative_reward / max(self._current_step, 1), 4),
            "unique_items_used": len(self._used_items),
            "budget_used": round(self._task_config["budget"] - self._budget, 2),
        }
