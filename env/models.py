"""
Pydantic typed models for the StyleSenseEnv OpenEnv environment.
Observation, Action, and Reward models for the step()/reset()/state() API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


# ═══════════════════════════════════════════
#  ENUMS
# ═══════════════════════════════════════════

class BodyType(str, Enum):
    PEAR = "pear"
    APPLE = "apple"
    HOURGLASS = "hourglass"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"
    ATHLETIC = "athletic"


class Occasion(str, Enum):
    JOB_INTERVIEW = "job_interview"
    CASUAL_OUTING = "casual_outing"
    FORMAL_DINNER = "formal_dinner"
    WEDDING_GUEST = "wedding_guest"
    GYM_WORKOUT = "gym_workout"
    DATE_NIGHT = "date_night"
    BUSINESS_MEETING = "business_meeting"
    COLLEGE_CLASS = "college_class"
    FESTIVAL = "festival"
    FUNERAL = "funeral"


class Season(str, Enum):
    SUMMER = "summer"
    WINTER = "winter"
    MONSOON = "monsoon"
    SPRING = "spring"
    AUTUMN = "autumn"


class CulturalContext(str, Enum):
    WESTERN = "western"
    INDO_WESTERN = "indo_western"
    TRADITIONAL_INDIAN = "traditional_indian"
    EAST_ASIAN = "east_asian"
    MIDDLE_EASTERN = "middle_eastern"
    AFRICAN = "african"


class FitType(str, Enum):
    SLIM = "slim"
    REGULAR = "regular"
    RELAXED = "relaxed"
    TAILORED = "tailored"
    OVERSIZED = "oversized"


class ClothingCategory(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    OUTERWEAR = "outerwear"
    SHOES = "shoes"
    ACCESSORY = "accessory"


class PatternType(str, Enum):
    SOLID = "solid"
    STRIPED = "striped"
    FLORAL = "floral"
    CHECKED = "checked"
    ABSTRACT = "abstract"
    POLKA_DOT = "polka_dot"
    PAISLEY = "paisley"
    GEOMETRIC = "geometric"


# ═══════════════════════════════════════════
#  OBSERVATION MODELS
# ═══════════════════════════════════════════

class UserProfile(BaseModel):
    """User's body measurements and characteristics."""
    body_type: BodyType
    height_cm: float = Field(ge=120, le=230)
    weight_kg: float = Field(ge=30, le=200)
    shoulder_width_cm: float = Field(ge=15, le=80)
    waist_cm: float = Field(ge=40, le=160)
    hip_cm: float = Field(ge=50, le=180)
    skin_tone: str  # e.g., "warm_deep", "cool_light", "neutral_medium"
    age_group: str  # "teen", "young_adult", "adult", "senior"
    gender_presentation: str  # "masculine", "feminine", "androgynous"


class WeatherCondition(BaseModel):
    """Current weather state."""
    temperature_c: float = Field(ge=-10, le=50)
    humidity_percent: float = Field(ge=0, le=100)
    is_rainy: bool = False
    wind_speed_kmh: float = Field(ge=0, le=100)
    uv_index: float = Field(ge=0, le=12)


class TrendState(BaseModel):
    """Current fashion trend snapshot."""
    trending_colors: List[str]
    trending_styles: List[str]
    trending_patterns: List[str]
    trend_quarter: int = Field(ge=1, le=4)


class WardrobeItem(BaseModel):
    """A single clothing item in the wardrobe."""
    item_id: str
    category: ClothingCategory
    sub_category: str  # "shirt", "t_shirt", "blazer", "jeans", etc.
    color: str
    pattern: PatternType = PatternType.SOLID
    fit: FitType = FitType.REGULAR
    formality_level: int = Field(ge=0, le=10)  # 0=extremely casual, 10=black tie
    weather_suitability: List[Season]
    cultural_tags: List[str] = Field(default_factory=list)
    price: float = Field(ge=0)
    condition: float = Field(ge=0.0, le=1.0, default=1.0)  # 1.0=new, 0.0=worn out


class ScheduleEvent(BaseModel):
    """A single event in the day schedule."""
    time: str  # "09:00"
    occasion: Occasion
    duration_hours: float = 2.0
    location: str = "indoor"


class Observation(BaseModel):
    """Full observation the agent receives each step."""
    user_profile: UserProfile
    occasion: Occasion
    season: Season
    weather: WeatherCondition
    cultural_context: CulturalContext
    current_trends: TrendState
    wardrobe: List[WardrobeItem]
    budget_remaining: float = Field(ge=0)
    day_schedule: List[ScheduleEvent] = Field(default_factory=list)
    episode_step: int = 0
    max_steps: int = 1
    previous_outfits: List[Dict] = Field(default_factory=list)
    current_event_index: int = 0


# ═══════════════════════════════════════════
#  ACTION MODEL
# ═══════════════════════════════════════════

class BuyItem(BaseModel):
    """Request to buy a new item."""
    category: ClothingCategory
    sub_category: str
    color: str
    max_price: float = Field(ge=0)


class OutfitAction(BaseModel):
    """Action the agent takes: recommend an outfit."""
    top_item_id: str
    bottom_item_id: str
    shoes_item_id: str
    outerwear_item_id: Optional[str] = None
    accessories: List[str] = Field(default_factory=list, max_length=3)
    color_palette_reasoning: str = ""
    fit_reasoning: str = ""
    buy_new_items: List[BuyItem] = Field(default_factory=list)


# ═══════════════════════════════════════════
#  REWARD MODEL
# ═══════════════════════════════════════════

class RewardBreakdown(BaseModel):
    """Detailed reward with partial progress signals."""
    occasion_appropriateness: float = Field(ge=0.0, le=1.0, default=0.0)
    body_type_flattery: float = Field(ge=0.0, le=1.0, default=0.0)
    color_harmony: float = Field(ge=0.0, le=1.0, default=0.0)
    weather_suitability: float = Field(ge=0.0, le=1.0, default=0.0)
    cultural_compliance: float = Field(ge=0.0, le=1.0, default=0.0)
    trend_alignment: float = Field(ge=0.0, le=1.0, default=0.0)
    budget_efficiency: float = Field(ge=0.0, le=1.0, default=0.0)
    outfit_variety: float = Field(ge=0.0, le=1.0, default=0.0)
    comfort_score: float = Field(ge=0.0, le=1.0, default=0.0)
    total_reward: float = 0.0
    penalties: Dict[str, float] = Field(default_factory=dict)
    feedback_message: str = ""


# ═══════════════════════════════════════════
#  API RESPONSE MODELS
# ═══════════════════════════════════════════

class StepResponse(BaseModel):
    """Response from the step() endpoint."""
    observation: Observation
    reward: RewardBreakdown
    done: bool
    info: Dict = Field(default_factory=dict)


class GraderResponse(BaseModel):
    """Response from the grader endpoint."""
    task_id: str
    score: float = Field(ge=0.0, le=1.0)
    breakdown: Dict = Field(default_factory=dict)
    passed: bool = False


class TaskInfo(BaseModel):
    """Information about a task."""
    id: str
    name: str
    description: str
    difficulty: str
    max_steps: int
    action_schema: Dict


class BaselineResponse(BaseModel):
    """Response from the baseline endpoint."""
    scores: Dict[str, float]
    details: Dict = Field(default_factory=dict)
