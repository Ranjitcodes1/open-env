"""
Deterministic graders for StyleSenseEnv tasks.
Uses centralized thresholds from config.py.
"""

from typing import Dict
from env.config import PASSING_THRESHOLDS


def grade_easy(episode_summary: Dict) -> Dict:
    """Grade 'easy' task: Single outfit match."""
    avg_reward = max(0.01, min(0.99, episode_summary.get("average_reward", 0.0)))
    threshold = PASSING_THRESHOLDS["easy"]
    
    passed = avg_reward >= threshold
    return {
        "score": avg_reward,
        "passed": passed,
        "breakdown": {"avg_reward": avg_reward, "threshold": threshold},
    }


def grade_medium(episode_summary: Dict) -> Dict:
    """Grade 'medium' task: 4 events, variety check."""
    avg_reward = episode_summary.get("average_reward", 0.0)
    unique_items = episode_summary.get("unique_items_used", 0)
    threshold = PASSING_THRESHOLDS["medium"]

    # Penalty if variety is extremely low
    final_score = avg_reward
    if unique_items < 5:
        final_score *= 0.8
    
    final_score = max(0.01, min(0.99, final_score))
    passed = final_score >= threshold
    return {
        "score": round(final_score, 4),
        "passed": passed,
        "breakdown": {
            "avg_reward": avg_reward,
            "unique_items": unique_items,
            "threshold": threshold,
        },
    }


def grade_hard(episode_summary: Dict) -> Dict:
    """Grade 'hard' task: 21 events, budget and trends."""
    avg_reward = max(0.01, min(0.99, episode_summary.get("average_reward", 0.0)))
    budget_used = episode_summary.get("budget_used", 0.0)
    threshold = PASSING_THRESHOLDS["hard"]

    passed = avg_reward >= threshold
    return {
        "score": avg_reward,
        "passed": passed,
        "breakdown": {
            "avg_reward": avg_reward,
            "budget_used": budget_used,
            "threshold": threshold,
        },
    }


def grade(env, task_id: str) -> Dict:
    """Consolidated grading function."""
    summary = env.get_episode_summary()
    graders = {
        "easy": grade_easy,
        "medium": grade_medium,
        "hard": grade_hard,
    }
    grader_func = graders.get(task_id)
    if not grader_func:
        raise ValueError(f"No grader for task: {task_id}")
    return grader_func(summary)
