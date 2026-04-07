"""
OpenEnv evaluation script for StyleSense.
Handles LLM-based styling recommendations with structured logging.
"""

import os
import json
import time
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI
from env.models import OutfitAction

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

BENCHMARK = "StyleSenseEnv"

# Environment URL (Local or Remote)
ENV_URL = os.environ.get("STYLESENSE_URL", "http://localhost:7860")

# Initialize OpenAI-compliant client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

def format_observation(obs: Dict[str, Any]) -> str:
    """Format observation for LLM context."""
    return json.dumps({
        "user_profile": obs["user_profile"],
        "occasion": obs["occasion"],
        "season": obs["season"],
        "weather": obs["weather"],
        "current_trends": obs["current_trends"],
        "wardrobe_size": len(obs["wardrobe"]),
        "budget_remaining": obs["budget_remaining"],
        "episode_step": obs["episode_step"],
        "max_steps": obs["max_steps"]
    }, indent=2)

def get_styling_recommendation(obs: Dict[str, Any]) -> OutfitAction:
    """Query the LLM for a styling recommendation."""
    prompt = f"""
    You are an expert fashion stylist. Based on the following environment state, recommend the best possible outfit.
    You must return a JSON object that strictly follows the 'OutfitAction' schema.
    
    ENVIRONMENT STATE:
    {format_observation(obs)}
    
    RESPONSE FORMAT:
    {{
        "top_item_id": "...",
        "bottom_item_id": "...",
        "shoes_item_id": "...",
        "outerwear_item_id": "...", (optional)
        "accessories": ["...", "..."], (max 3)
        "color_palette_reasoning": "...",
        "fit_reasoning": "...",
        "buy_new_items": [] (empty unless explicitly needed for a task)
    }}
    
    Available Wardrobe:
    {json.dumps([{"id": i["item_id"], "cat": i["category"], "sub": i["sub_category"], "color": i["color"]} for i in obs["wardrobe"][:20]], indent=1)}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        return OutfitAction(**data)
    except Exception as e:
        # Fallback to a simple rule-based selection if LLM fails
        print(f"LLM Error: {e}, using fallback.", flush=True)
        return OutfitAction(
            top_item_id=obs["wardrobe"][0]["item_id"],
            bottom_item_id=obs["wardrobe"][1]["item_id"],
            shoes_item_id=obs["wardrobe"][2]["item_id"],
            color_palette_reasoning="Fallback due to LLM error"
        )

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Replace spaces with underscores or remove them strictly, the example shows no spaces in action strings ideally, 
    # but since our action is an object, we'll format it simply. We'll stringify the top/bottom/shoes IDs without spaces.
    action_str = action.replace(" ", "")
    print(
        f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def run_episode(task_id: str):
    """Execute a single task episode."""
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    # 1. Reset
    resp = requests.post(f"{ENV_URL}/reset", params={"task_id": task_id})
    if resp.status_code != 200:
        print(f"Error resetting: {resp.text}", flush=True)
        return
    
    obs = resp.json()
    done = False
    step_num = 1
    rewards = []
    success = False
    score = 0.0
    
    # 2. Main Step Loop
    while not done:
        # Get recommendation
        action = get_styling_recommendation(obs)
        action_dict = action.model_dump()
        
        step_resp = requests.post(f"{ENV_URL}/step", json=action_dict)
        error_val = None
        
        if step_resp.status_code != 200:
            error_val = step_resp.text
            done = True
            reward = 0.0
            rewards.append(reward)
            log_step(step=step_num, action="error", reward=reward, done=done, error=error_val)
            break
            
        result = step_resp.json()
        reward = result["reward"]["total_reward"]
        done = result["done"]
        rewards.append(reward)
        
        act_str = f"outfit({action.top_item_id},{action.bottom_item_id},{action.shoes_item_id})"
        log_step(step=step_num, action=act_str, reward=reward, done=done, error=error_val)
        
        obs = result["observation"]
        if done:
            break
        step_num += 1
        
    # 3. Grading
    grade_resp = requests.post(f"{ENV_URL}/grader", params={"task_id": task_id})
    if grade_resp.status_code == 200:
        grade_data = grade_resp.json()
        score = grade_data["score"]
        success = grade_data["passed"]
    
    log_end(success=success, steps=step_num, score=score, rewards=rewards)

def main():
    tasks = ["easy", "medium", "hard"]
    for tid in tasks:
        run_episode(tid)

if __name__ == "__main__":
    main()
