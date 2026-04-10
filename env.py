from typing import Any, Optional, TypeVar, Dict, Tuple
from models import SupportObservation, SupportAction, SupportReward
from graders import SupportGrader, LLMGrader, TASKS

class SupportEnv:
    """
    Customer Support Automation Environment — OpenEnv Standard Compliant.
    
    Implements the standard OpenEnv interface:
      - reset()  → Returns initial observation
      - step()   → Processes action, returns (obs, reward, done, info)
      - state()  → Returns current environment state
      - close()  → Cleanup
    """

    def __init__(self, use_llm_grading: bool = False):
        self.current_task_idx = -1
        self.use_llm_grading = use_llm_grading
        self._state: Dict[str, Any] = {
            "task_id": None,
            "ticket_text": None,
            "history": [],
            "total_tasks": len(TASKS)
        }

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any
    ) -> SupportObservation:
        """Resets to the next task in the list (cycles back)."""
        self.current_task_idx = (self.current_task_idx + 1) % len(TASKS)
        task = TASKS[self.current_task_idx]

        self._state = {
            "task_id": task["id"],
            "ticket_text": task["ticket_text"],
            "history": [],
            "total_tasks": len(TASKS)
        }

        return SupportObservation(
            ticket_text=task["ticket_text"],
            metadata={
                "task_id": task["id"],
                "difficulty": self._get_difficulty(),
                "task_number": self.current_task_idx + 1,
                "total_tasks": len(TASKS)
            }
        )

    def step(
        self,
        action: SupportAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any
    ) -> Tuple[SupportObservation, SupportReward, bool, Dict[str, Any]]:
        """Executes one step in the environment."""
        task = TASKS[self.current_task_idx]
        difficulty = self._get_difficulty()

        # Programmatic grading based on difficulty
        if difficulty == "easy":
            reward = SupportGrader.grade_task_easy(action, task["ground_truth"])
        elif difficulty == "medium":
            reward = SupportGrader.grade_task_medium(action, task["ground_truth"])
        else:
            reward = SupportGrader.grade_task_hard(action, task["ground_truth"])

        # Optional LLM-based grading for hard tasks (blended score)
        if self.use_llm_grading and difficulty == "hard" and action.resolution_steps:
            action_text = " | ".join(action.resolution_steps)
            llm_score, llm_feedback = LLMGrader.grade_with_llm(action_text, task["ticket_text"])
            # Blend: 60% programmatic + 40% LLM
            blended_score = round(0.6 * reward.score + 0.4 * llm_score, 2)
            reward = SupportReward(
                score=blended_score,
                feedback=f"{reward.feedback} {llm_feedback}",
                done=True
            )

        observation = SupportObservation(
            ticket_text=task["ticket_text"],
            metadata={"status": "completed", "task_id": task["id"]}
        )

        # Record in history
        self._state["history"].append({
            "task_id": task["id"],
            "score": reward.score,
            "feedback": reward.feedback
        })

        return observation, reward, reward.done, {"task_id": task["id"]}

    def state(self) -> Dict[str, Any]:
        """Returns the current environment state."""
        return self._state

    def _get_difficulty(self) -> str:
        task_id = TASKS[self.current_task_idx]["id"]
        if "easy" in task_id:
            return "easy"
        if "medium" in task_id:
            return "medium"
        return "hard"

    def close(self) -> None:
        """Cleanup resources."""
        pass
