import os
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from models import SupportAction, SupportReward

class SupportGrader:
    """Programmatic graders for customer support tasks."""

    @staticmethod
    def grade_task_easy(action: SupportAction, ground_truth: Dict[str, Any]) -> SupportReward:
        """Categorization - Easy: Exact match on category."""
        score = 0.0
        feedback = "Incorrect classification."
        if action.classification and action.classification.lower() == ground_truth["category"].lower():
            score = 1.0
            feedback = "Correct classification!"
        return SupportReward(score=score, feedback=feedback, done=True)

    @staticmethod
    def grade_task_medium(action: SupportAction, ground_truth: Dict[str, Any]) -> SupportReward:
        """Extraction - Medium: Check order_id and sentiment."""
        total_score = 0.0
        feedback_parts = []

        # Check order_id
        if action.order_id and action.order_id.replace("#", "") == ground_truth["order_id"].replace("#", ""):
            total_score += 0.5
            feedback_parts.append("Order ID correct.")
        else:
            feedback_parts.append(f"Order ID incorrect. Expected: {ground_truth['order_id']}.")

        # Check sentiment
        if action.sentiment and action.sentiment.lower() == ground_truth["sentiment"].lower():
            total_score += 0.5
            feedback_parts.append("Sentiment correct.")
        else:
            feedback_parts.append(f"Sentiment incorrect. Expected: {ground_truth['sentiment']}.")

        return SupportReward(score=total_score, feedback=" ".join(feedback_parts), done=True)

    @staticmethod
    def grade_task_hard(action: SupportAction, ground_truth: Dict[str, Any]) -> SupportReward:
        """Resolution - Hard: Check keyword coverage and minimum steps."""
        if not action.resolution_steps or len(action.resolution_steps) < 2:
            return SupportReward(score=0.0, feedback="Incomplete resolution plan. At least 2 steps required.", done=True)

        feedback_parts = []

        # Check required keywords
        keywords_met = 0
        required = ground_truth["required_keywords"]
        for kw in required:
            if any(kw.lower() in step.lower() for step in action.resolution_steps):
                keywords_met += 1

        keyword_score = keywords_met / len(required) if required else 0

        # Bonus for thoroughness (more steps = better, capped)
        step_bonus = min(0.1, len(action.resolution_steps) * 0.02)

        total_score = min(1.0, keyword_score + step_bonus)

        feedback_parts.append(f"Keyword match: {keywords_met}/{len(required)}.")
        feedback_parts.append(f"Steps provided: {len(action.resolution_steps)}.")

        return SupportReward(score=round(total_score, 2), feedback=" ".join(feedback_parts), done=True)


class LLMGrader:
    """LLM-based grader using Meta Llama via HuggingFace for qualitative evaluation."""

    @staticmethod
    def grade_with_llm(
        action_text: str,
        ticket_text: str,
        hf_token: Optional[str] = None
    ) -> Tuple[float, str]:
        """
        Use Meta Llama to evaluate the quality of a support resolution.
        Returns (score, feedback) tuple.
        """
        token = hf_token or os.getenv("HF_TOKEN")
        if not token:
            return 0.5, "LLM grading skipped: HF_TOKEN not available."

        try:
            from huggingface_hub import InferenceClient

            client = InferenceClient(
                model="meta-llama/Llama-3.1-8B-Instruct",
                token=token
            )

            prompt = f"""You are an expert customer support quality evaluator.

Rate the following agent response to a customer ticket on a scale of 0.0 to 1.0.

Customer Ticket: "{ticket_text}"

Agent Resolution: "{action_text}"

Consider these criteria:
1. Empathy and tone (0.2 weight)
2. Correctness of the solution (0.4 weight)
3. Completeness and actionability (0.2 weight)
4. Professionalism (0.2 weight)

Respond in this exact JSON format:
{{"score": 0.0, "feedback": "Brief explanation of the score"}}

Respond with ONLY the JSON object."""

            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:-1])

            result = json.loads(raw)
            score = max(0.0, min(1.0, float(result.get("score", 0.5))))
            feedback = result.get("feedback", "LLM evaluation complete.")
            return score, f"[LLM] {feedback}"

        except Exception as e:
            return 0.5, f"LLM grading failed: {str(e)}"


# ============================================================
# Task Definitions — 9 tasks across 3 difficulty levels
# ============================================================

TASKS = [
    # --- EASY: Ticket Classification ---
    {
        "id": "easy_1",
        "ticket_text": "Hey, I noticed a double charge for my last subscription payment. Can you fix it?",
        "ground_truth": {"category": "Billing"}
    },
    {
        "id": "easy_2",
        "ticket_text": "My account is locked after too many failed login attempts. I need to regain access immediately.",
        "ground_truth": {"category": "Account"}
    },
    {
        "id": "easy_3",
        "ticket_text": "The software keeps crashing whenever I try to export reports to PDF. This started after the last update.",
        "ground_truth": {"category": "Technical"}
    },

    # --- MEDIUM: Entity Extraction ---
    {
        "id": "medium_1",
        "ticket_text": "Order #44551 still hasn't arrived. I'm extremely frustrated as I needed it for a birthday! - Jane S.",
        "ground_truth": {"order_id": "44551", "sentiment": "Frustrated"}
    },
    {
        "id": "medium_2",
        "ticket_text": "Hi, just checking on order #78832. No rush, but it would be nice to get an estimated delivery date. Thanks!",
        "ground_truth": {"order_id": "78832", "sentiment": "Neutral"}
    },
    {
        "id": "medium_3",
        "ticket_text": "Where is my order #91204?! I paid for express shipping and it's been 2 weeks! This is completely unacceptable!",
        "ground_truth": {"order_id": "91204", "sentiment": "Frustrated"}
    },

    # --- HARD: Resolution Planning ---
    {
        "id": "hard_1",
        "ticket_text": "The blender I ordered arrived with a broken glass jar. I need a solution immediately. This is my third order from you guys and I'm very disappointed.",
        "ground_truth": {"required_keywords": ["refund", "replacement", "return label", "apologize"]}
    },
    {
        "id": "hard_2",
        "ticket_text": "I was charged twice for the same item AND it arrived damaged. I want a full refund and someone to explain how this happened. I'm considering leaving a public review.",
        "ground_truth": {"required_keywords": ["refund", "apologize", "investigate", "escalate"]}
    },
    {
        "id": "hard_3",
        "ticket_text": "My premium subscription was downgraded without notice, and I've lost access to features I was paying for. I need this fixed now or I'm cancelling everything.",
        "ground_truth": {"required_keywords": ["restore", "apologize", "compensation", "escalate"]}
    },
]
