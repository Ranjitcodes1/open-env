"""
Gymnasium wrapper for StyleSenseEnv to support standard RL training.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from env.style_env import StyleSenseEnv
from env.models import OutfitAction, ClothingCategory

class StyleSenseGymEnv(gym.Env):
    def __init__(self, task_id="easy"):
        super(StyleSenseGymEnv, self).__init__()
        self.raw_env = StyleSenseEnv(seed=42)
        self.task_id = task_id
        
        # We'll use a fixed-size action space for training simplicity
        # Mapping 5 tops, 5 bottoms, 5 shoes -> 125 discrete actions
        self.num_each = 6
        self.action_space = spaces.Discrete(self.num_each ** 3)
        
        # Observation space: simplified vector for the NN
        # (BodyType + Occasion + Season + Color Match features)
        self.observation_space = spaces.Box(low=-1, high=10, shape=(10,), dtype=np.float32)

    def _get_obs(self, obs):
        # Translate complex Observation model to simple float array
        # (Mock implementation for demo training)
        return np.array([
            len(obs.wardrobe), 
            obs.budget_remaining / 500.0,
            obs.episode_step,
            float(len(obs.occasion.value) % 10), # Numerical proxy for occasion
            float(len(obs.user_profile.body_type.value) % 10),
            0.0, 0.0, 0.0, 0.0, 0.0
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs = self.raw_env.reset(task_id=self.task_id, seed=seed)
        
        # Map wardrobe items to slots
        self.tops = [i for i in obs.wardrobe if i.category == ClothingCategory.TOP]
        self.bottoms = [i for i in obs.wardrobe if i.category == ClothingCategory.BOTTOM]
        self.shoes = [i for i in obs.wardrobe if i.category == ClothingCategory.SHOES]
        
        return self._get_obs(obs), {}

    def step(self, action):
        # 1. Unpack discrete action
        t_idx = (action // (self.num_each ** 2)) % len(self.tops) if self.tops else 0
        b_idx = (action // self.num_each) % len(self.bottoms) if self.bottoms else 0
        s_idx = action % len(self.shoes) if self.shoes else 0
        
        # 2. Build OutfitAction
        outfit = OutfitAction(
            top_item_id=self.tops[t_idx].item_id if self.tops else "none",
            bottom_item_id=self.bottoms[b_idx].item_id if self.bottoms else "none",
            shoes_item_id=self.shoes[s_idx].item_id if self.shoes else "none",
            color_palette_reasoning="PPO Agent choice"
        )
        
        # 3. Environment Step
        obs, reward_breakdown, done, info = self.raw_env.step(outfit)
        
        reward = reward_breakdown.total_reward
        truncated = False
        
        return self._get_obs(obs), float(reward), done, truncated, info
