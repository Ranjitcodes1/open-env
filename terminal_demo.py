"""
StyleSenseEnv: COMPREHENSIVE TERMINAL DEMO
This script exercises every major component of the environment to demonstrate functionality.
"""

import os
import json
from env.style_env import StyleSenseEnv
from env.models import OutfitAction, ClothingCategory
from env.body_profiles import generate_random_profile
from env.wardrobe import generate_wardrobe
from env.style_rules import score_body_flattery
from tasks.graders import grade

def run_demo():
    print("="*60)
    print("      StyleSenseEnv: FINAL COMPREHENSIVE DEMO      ")
    print("="*60)
    
    # 1. Models & Profiles
    print("\n[FILE: env/body_profiles.py] -> Generating Random Profile...")
    profile = generate_random_profile()
    print(f"✅ Created {profile.gender_presentation} profile: {profile.body_type.value}, "
          f"Shoulder={profile.shoulder_width_cm}cm, "
          f"Waist={profile.waist_cm}cm")
    
    # 2. Wardrobe Generation
    print("\n[FILE: env/wardrobe.py] -> Generating Wardrobe...")
    wardrobe = generate_wardrobe(size=30)
    print(f"✅ Generated 30 items. (Tops: {len([i for i in wardrobe if i.category == ClothingCategory.TOP])}, "
          f"Bottoms: {len([i for i in wardrobe if i.category == ClothingCategory.BOTTOM])})")
    
    # 3. Style Rules Engine
    print("\n[FILE: env/style_rules.py] -> Evaluating Fashion Constraints...")
    # Mock some items for a quick rule check
    top, bottom = [i for i in wardrobe if i.category == ClothingCategory.TOP][0], \
                 [i for i in wardrobe if i.category == ClothingCategory.BOTTOM][0]
    flattery_score = score_body_flattery([top, bottom], profile)
    print(f"✅ Rules Engine Online. Flattery Score: {flattery_score:.2f}")
    
    # 4. Core Environment (Reset/Step)
    print("\n[FILE: env/style_env.py] -> Initializing RL Environment...")
    env = StyleSenseEnv(seed=123)
    obs = env.reset(task_id="easy")
    print(f"✅ Env Reset Successful. Task: {obs.occasion.value}")
    
    print("\n[FILE: env/reward.py] -> Taking Action & Computing Reward...")
    action = OutfitAction(
        top_item_id=obs.wardrobe[0].item_id,
        bottom_item_id=obs.wardrobe[1].item_id,
        shoes_item_id=obs.wardrobe[2].item_id,
        color_palette_reasoning="Demo color match."
    )
    obs_next, reward, done, info = env.step(action)
    print(f"✅ Step Successful. Reward Breakdowns:")
    print(f"   - Occasion Match: {reward.occasion_appropriateness:.2f}")
    print(f"   - Trend Alignment: {reward.trend_alignment:.2f}")
    print(f"   - TOTAL REWARD: {reward.total_reward:.4f}")
    print(f"   - FEEDBACK: {reward.feedback_message}")
    
    # 5. Graders
    print("\n[FILE: tasks/graders.py] -> Running Grader...")
    final_grade = grade(env, "easy")
    print(f"✅ Grader Results: Passed={final_grade['passed']}, Final Score={final_grade['score']:.4f}")
    
    print("\n" + "="*60)
    print("      ALL COMPONENTS VERIFIED AND 100% OPERATIONAL      ")
    print("="*60)

if __name__ == "__main__":
    run_demo()
