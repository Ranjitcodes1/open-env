---
title: StyleSenseEnv
emoji: 👗
colorFrom: pink
colorTo: blue
sdk: docker
pinned: false
---

# StyleSenseEnv - Professional OpenEnv Submission

AI-powered styling recommendation environment for OpenEnv. This project simulates a high-fidelity, sequential decision-making task where an AI agent acts as a personal stylist.

## Key Features
- **Production-Grade RL Architecture**: Optimized for performance with O(1) item resolution and wardrobe caching.
- **Multi-Objective Reward Engine**: Evaluates 9 dimensions (Occasion, Body Type, Color Harmony, Trends, Weather, etc.).
- **Built-in RL Training**: Integrated with **Stable Baselines 3 (PPO)**. See `train_rl.py` and `training_performance.png`.
- **Pre-Submission Validated**: Includes `validator.py` ensuring 100% compliance with automated grading systems.
- **FastAPI Backend**: Fully typed endpoints for `/reset`, `/step`, `/state`, `/tasks`, and `/grader`.

## Project Structure
- `env/`: Core simulation logic, models, and fashion engines.
- `tasks/`: Task-specific graders and configurations.
- `inference.py`: **[MANDATORY]** Submission script with structured logging.
- `train_rl.py`: Training pipeline using PPO.
- `validator.py`: Pre-submission check tool.
- `Dockerfile`: Configured for HF Spaces (vCPU=2, 8GB RAM).

## Installation and Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Local Validation (Recommended before submission)
python validator.py

# 3. Start the Simulation Server
uvicorn server:app --host 0.0.0.0 --port 7860
```

## Training and Baseline
You can train a neural network agent to handle the styling tasks:
```bash
python train_rl.py
```
This will output a `training_performance.png` graph showing the agent's learning curve.

### Baseline Scores (Reproduce via /baseline)
| Task | Difficulty | Baseline Score |
| :--- | :---: | :---: |
| Easy | 1 | 0.63 |
| Medium | 2 | 0.80 |
| Hard | 3 | 0.58 |

### Baseline Analysis
The **Easy** task is a "one-shot" challenge (1 step), making it highly sensitive to the initial wardrobe-occasion match. A single mismatch leads to a lower score. The **Medium** task (4 steps) allows the agent to average out its performance across multiple events. Our `RuleBasedAgent` is highly consistent at color/formality matching, allowing it to maintain a higher average over several steps. The **Hard** task remains the most difficult due to budget limits and trend shifts over 21 steps.

## Reward Logic
The environment calculates rewards based on 9 critical fashion factors:
- **Occasion Appropriateness**: Matching dress codes (e.g., Casual vs. Formal Dinner).
- **Body Type Flattery**: Using `env/style_rules.py` to check silhouettes (Pear, Apple, etc.).
- **Color Harmony**: Scientific scoring of color pairs based on complementary theory.
- **Trend Alignment**: Adapting to non-stationary trend shifts.
- **Penalties**: Handled for budget breaches, missing items, or weather mismatches.

## Submission Compliance
This repo follows the strict OpenEnv requirements:
- `inference.py` in root.
- Emits structured `[START]`, `[STEP]`, and `[END]` logs.
- Uses `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN` environment variables.
- Verified on a 2vCPU / 8GB RAM environment.

## License
MIT
