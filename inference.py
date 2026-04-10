import os
import json
import requests
from typing import List, Dict, Any
from huggingface_hub import InferenceClient

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
HF_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face token from hf.co/settings/tokens

# Use Meta's Llama model via HuggingFace Inference API
client = InferenceClient(
    model="meta-llama/Llama-3.1-8B-Instruct",
    token=HF_TOKEN
)

def get_agent_response(ticket_text: str, difficulty: str) -> Dict[str, Any]:
    """Baseline agent using Meta's Llama model via HuggingFace Inference API."""
    prompt = f"""You are a customer support AI assistant.
Current Ticket: "{ticket_text}"
Difficulty: {difficulty}

Task:
- If difficulty is 'easy', provide 'classification' (one of: Billing, Technical, Account).
- If difficulty is 'medium', provide 'order_id' (just the number, e.g. 44551) and 'sentiment' (Frustrated or Neutral).
- If difficulty is 'hard', provide a list of 'resolution_steps' to help the customer.

Respond STRICTLY in valid JSON format with ONLY the fields matching the task difficulty:
For easy: {{"classification": "..."}}
For medium: {{"order_id": "...", "sentiment": "..."}}
For hard: {{"resolution_steps": ["step 1", "step 2", ...]}}

Important: Include keywords like 'refund', 'replacement', 'return label', 'apologize' in resolution steps when relevant.
Respond with ONLY the JSON object, no other text."""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1  # Low temperature for consistent structured output
    )

    raw_content = response.choices[0].message.content.strip()
    
    # Handle cases where the model wraps JSON in markdown code blocks
    if raw_content.startswith("```"):
        lines = raw_content.split("\n")
        raw_content = "\n".join(lines[1:-1])  # Strip ```json and ``` markers
    
    return json.loads(raw_content)

def main():
    total_score = 0.0
    tasks_run = 0

    print(f"Starting baseline inference at {API_URL}...")
    print(f"Using model: meta-llama/Llama-3.1-8B-Instruct via HuggingFace\n")

    # Get total available tasks from backend
    root_resp = requests.get(f"{API_URL}/")
    root_data = root_resp.json()
    task_ids = root_data.get("tasks", [])
    tasks_count = len(task_ids)

    for i in range(tasks_count):
        print(f"\n{'='*50}")
        print(f"--- Task {i+1}/{tasks_count} ---")

        # Reset environment
        reset_resp = requests.post(f"{API_URL}/reset")
        obs = reset_resp.json()
        ticket_text = obs["ticket_text"]
        difficulty = obs["metadata"]["difficulty"]

        print(f"Task ID:    {obs['metadata'].get('task_id', 'N/A')}")
        print(f"Difficulty: {difficulty}")
        print(f"Ticket:     {ticket_text[:80]}...")

        # Get AI response from Meta Llama
        try:
            ai_action_data = get_agent_response(ticket_text, difficulty)
            print(f"AI Action:  {ai_action_data}")
        except Exception as e:
            print(f"AI Error: {e}")
            ai_action_data = {}

        # Step in environment
        step_resp = requests.post(f"{API_URL}/step", json=ai_action_data)
        result = step_resp.json()

        reward = result["reward"]["score"]
        feedback = result["reward"]["feedback"]

        print(f"Score:      {reward}")
        print(f"Feedback:   {feedback}")

        total_score += reward
        tasks_run += 1

    avg_score = total_score / tasks_run if tasks_run > 0 else 0
    print(f"\n{'='*50}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*50}")
    print(f"Tasks Completed:    {tasks_run}/{tasks_count}")
    print(f"Total Score:        {total_score:.2f}")
    print(f"Average Score:      {avg_score:.2f}")
    print(f"Model Used:         meta-llama/Llama-3.1-8B-Instruct")
    print(f"{'='*50}")

if __name__ == "__main__":
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set.")
        print("Get your token from: https://huggingface.co/settings/tokens")
    else:
        main()
