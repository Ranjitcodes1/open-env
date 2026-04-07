"""
FastAPI server for StyleSense OpenEnv.
Exposes standard endpoints for remote evaluation.
"""

import os
import uvicorn
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from env.style_env import StyleSenseEnv, TASK_CONFIGS
from env.models import (
    OutfitAction, StepResponse, GraderResponse, TaskInfo,
    BaselineResponse, Observation,
)
from tasks.graders import grade
from env.config import DEFAULT_SEED

app = FastAPI(
    title="StyleSenseEnv",
    description="AI-Powered Styling Recommendation OpenEnv Environment",
    version="1.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env = StyleSenseEnv(seed=DEFAULT_SEED)


@app.get("/")
async def root():
    """Redirect to interactive documentation."""
    return RedirectResponse(url="/docs")


@app.post("/reset", response_model=Observation)
async def reset(
    task_id: str = Query(default="easy", description="Task difficulty"),
    seed: Optional[int] = Query(default=None, description="Optional random seed")
):
    """Reset for a specific task."""
    try:
        return env.reset(task_id=task_id, seed=seed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step", response_model=StepResponse)
async def step(action: OutfitAction):
    """Take a styling action and receive feedback."""
    try:
        observation, reward, done, info = env.step(action)
        return StepResponse(
            observation=observation,
            reward=reward,
            done=done,
            info=info,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/state")
async def state():
    """Return current environment state snapshot."""
    return env.state()


@app.get("/tasks", response_model=List[TaskInfo])
async def tasks():
    """Return list of tasks with action schemas."""
    task_list = []
    for task_id, config in TASK_CONFIGS.items():
        task_list.append(TaskInfo(
            id=task_id,
            name=config["name"],
            description=config["description"],
            difficulty=config["difficulty"],
            max_steps=config["max_steps"],
            action_schema=OutfitAction.model_json_schema(),
        ))
    return task_list


@app.post("/grader", response_model=GraderResponse)
async def grader(task_id: str = Query(default="easy", description="Task to grade")):
    """Score the current episode."""
    try:
        result = grade(env, task_id)
        return GraderResponse(
            task_id=task_id,
            score=result["score"],
            breakdown=result["breakdown"],
            passed=result["passed"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/baseline", response_model=BaselineResponse)
async def baseline():
    """Execute rule-based baseline across all tasks."""
    from baseline.rule_based_agent import RuleBasedAgent

    agent = RuleBasedAgent()
    scores = {}
    details = {}

    for t_id in ["easy", "medium", "hard"]:
        task_env = StyleSenseEnv(seed=DEFAULT_SEED)
        obs = task_env.reset(task_id=t_id)

        done = False
        step_count = 0
        while not done:
            action = agent.act(obs)
            obs, reward, done, info = task_env.step(action)
            step_count += 1

        result = grade(task_env, t_id)
        scores[t_id] = result["score"]
        details[t_id] = {
            "score": result["score"],
            "passed": result["passed"],
            "breakdown": result["breakdown"],
            "steps": step_count,
        }

    return BaselineResponse(scores=scores, details=details)


def main():
    """Entry point for the server script."""
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
