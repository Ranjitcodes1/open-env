"""
StyleSenseEnv: RL Training Demo
Uses Stable Baselines 3 (PPO) to learn styling logic.
Generates a training loss/reward graph.
"""

import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import time
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from env.gym_wrapper import StyleSenseGymEnv

class RewardLogger(BaseCallback):
    """Callback to track rewards for plotting."""
    def __init__(self, verbose=0):
        super(RewardLogger, self).__init__(verbose)
        self.rewards = []

    def _on_step(self) -> bool:
        if 'rewards' in self.locals:
            r = self.locals['rewards'][0]
            self.rewards.append(r)
        return True

def train():
    print("--- Starting RL Training: StyleSenseEnv (PPO) ---")
    
    # 1. Initialize Wrapper
    env = StyleSenseGymEnv(task_id="easy")
    
    # 2. Configure PPO Agent
    # We use a simple MLP Policy (Multi-Layer Perceptron)
    # The 'Loss Function' for PPO includes a Policy Gradient loss and a Value Function loss (MSE).
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=3e-4, batch_size=32)
    
    # 3. Training Loop (Small run for demo)
    callback = RewardLogger()
    total_timesteps = 1000
    print(f"Training for {total_timesteps} steps...")
    model.learn(total_timesteps=total_timesteps, callback=callback)
    
    # 4. Generate Training Curve (The 'Loss' equivalent)
    # In RL, we track cumulative Mean Reward as the inverse of loss.
    plt.figure(figsize=(10, 5))
    
    # Smoothing the rewards for better visibility
    window = 10
    smoothed_rewards = np.convolve(callback.rewards, np.ones(window)/window, mode='valid')
    
    plt.plot(smoothed_rewards, label='Smoothed Reward (Inverse Loss)')
    plt.title('StyleSenseEnv: PPO Training Performance')
    plt.xlabel('Training Steps')
    plt.ylabel('Style Accuracy (Reward)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Save to disk
    plt.savefig('training_performance.png')
    print("\n✅ Training Complete. Graph saved as 'training_performance.png'")

if __name__ == "__main__":
    train()
