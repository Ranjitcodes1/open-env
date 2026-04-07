"""
Verification script for StyleSenseEnv refactor.
Tests reset, step, and baseline functionality.
"""
from env.style_env import StyleSenseEnv
from baseline.rule_based_agent import RuleBasedAgent
import json

def verify():
    print("--- Starting StyleSenseEnv Verification ---")
    
    # 1. Test Reset
    print("\n1. Testing reset(task_id='easy')...")
    env = StyleSenseEnv(seed=42)
    obs = env.reset(task_id="easy")
    print(f"Observation built successfully. Wardrobe size: {len(obs.wardrobe)}")
    assert len(obs.wardrobe) >= 20
    
    # 2. Test Step with Baseline Agent
    print("\n2. Testing step() with RuleBasedAgent...")
    agent = RuleBasedAgent(seed=42)
    action = agent.act(obs)
    next_obs, reward, done, info = env.step(action)
    
    print(f"Action taken: Top={action.top_item_id}, Bottom={action.bottom_item_id}")
    print(f"Reward: {reward.total_reward}")
    print(f"Feedback: {reward.feedback_message}")
    print(f"Info: {info}")
    
    assert reward.total_reward >= -1.0
    assert done is True  # Easy task is 1 step
    
    # 3. Test Grading
    print("\n3. Testing grader...")
    from tasks.graders import grade
    result = grade(env, "easy")
    print(f"Grade Result: Passed={result['passed']}, Score={result['score']}")
    
    # 4. Test Configuration Caching
    print("\n4. Testing wardrobe_map caching...")
    assert hasattr(env, "_wardrobe_map")
    assert action.top_item_id in env._wardrobe_map
    print(f"Wardrobe map verified. Items cached: {len(env._wardrobe_map)}")

    print("\n--- Verification Successful! ---")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"\nVerification FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
