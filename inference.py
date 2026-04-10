import os
import json
import requests
from typing import List, Dict, Any
from openai import OpenAI

# Pre-Submission Checklist Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") # No default allowed per checklist

# Initialize OpenAI client with Hugging Face endpoint
client = OpenAI(
    base_url="https://api-inference.huggingface.co/v1/",
    api_key=HF_TOKEN
)

def get_agent_response(ticket_text: str, difficulty: str) -> Dict[str, Any]:
    """Agent using OpenAI-compatible client with Meta's Llama model."""
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
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1
    )

    raw_content = response.choices[0].message.content.strip()
    
    # Strip markdown if present
    if raw_content.startswith("```"):
        raw_content = raw_content.split("```")[1]
        if raw_content.startswith("json"):
            raw_content = raw_content[4:]
    
    return json.loads(raw_content)

def main():
    # [START]
    print("[START]")
    
    try:
        # Get total available tasks from backend
        root_resp = requests.get(f"{API_BASE_URL}/api")
        root_resp.raise_for_status()
        root_data = root_resp.json()
        task_ids = root_data.get("tasks", [])
        tasks_count = len(task_ids)
    except Exception as e:
        print(f"Failed to connect to environment at {API_BASE_URL}: {e}")
        return

    for i in range(tasks_count):
        # [STEP]
        print(f"[STEP] {i+1}/{tasks_count}")

        try:
            # Reset environment
            reset_resp = requests.post(f"{API_BASE_URL}/reset")
            obs = reset_resp.json()
            ticket_text = obs["ticket_text"]
            difficulty = obs["metadata"]["difficulty"]

            # Get AI response
            ai_action_data = get_agent_response(ticket_text, difficulty)

            # Step in environment
            requests.post(f"{API_BASE_URL}/step", json=ai_action_data)
        except Exception as e:
            # Continue to next step even if one fails
            pass

    # [END]
    print("[END]")

if __name__ == "__main__":
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set.")
    else:
        main()

