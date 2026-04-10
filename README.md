# SupportAutoEnv: Customer Support Automation for OpenEnv

SupportAutoEnv is a standardized execution environment for training and evaluating AI agents on real-world customer support tasks. Built on the **OpenEnv** specification by Meta & Hugging Face, it provides a range of scenarios from simple classification to complex resolution planning.

## Motivation

As AI agents move beyond toy problems, we need robust, reproducible benchmarks for practical utility. SupportAutoEnv simulates the daily workflow of a support representative, requiring the agent to understand context, extract critical data, and formulate actionable solutions.

## Features

- ✅ **OpenEnv Compliant** — Standard `reset()`, `step()`, `state()` interface
- ✅ **9 Tasks** across 3 difficulty levels (Easy, Medium, Hard)
- ✅ **Programmatic + LLM Grading** — Dual evaluation using keyword matching and Meta Llama
- ✅ **REST + WebSocket API** — Both HTTP and persistent WebSocket sessions
- ✅ **Meta Llama Baseline** — Inference agent powered by Llama-3.1-8B via HuggingFace
- ✅ **Interactive Dashboard** — Frontend UI for testing and visualization
- ✅ **Docker Ready** — One command to build and deploy

## Action and Observation Spaces

### Observation Space
The environment provides a `SupportObservation` object:
- `ticket_text` (str): The raw text of the incoming customer ticket.
- `metadata` (dict): Contextual info including `task_id`, `difficulty`, `task_number`, `total_tasks`.

### Action Space
The agent responds with a `SupportAction` object containing:
- `classification` (Optional[str]): Used for 'easy' tasks — one of `Billing`, `Technical`, `Account`.
- `order_id` (Optional[str]): Used for 'medium' tasks — extracted order number.
- `sentiment` (Optional[str]): Used for 'medium' tasks — `Frustrated` or `Neutral`.
- `resolution_steps` (Optional[List[str]]): Used for 'hard' tasks — multi-step resolution plan.

## Tasks & Difficulty (9 Tasks)

### Easy — Ticket Classification (3 tasks)
| Task | Ticket | Expected |
|:---|:---|:---|
| easy_1 | Double charge for subscription | Billing |
| easy_2 | Account locked after login attempts | Account |
| easy_3 | Software crashes on PDF export | Technical |

### Medium — Entity Extraction (3 tasks)
| Task | Ticket | Expected |
|:---|:---|:---|
| medium_1 | Order #44551 late, frustrated customer | order_id: 44551, sentiment: Frustrated |
| medium_2 | Order #78832 status check, calm tone | order_id: 78832, sentiment: Neutral |
| medium_3 | Order #91204 express late, angry | order_id: 91204, sentiment: Frustrated |

### Hard — Resolution Planning (3 tasks)
| Task | Ticket | Required Keywords |
|:---|:---|:---|
| hard_1 | Broken blender, repeat customer | refund, replacement, return label, apologize |
| hard_2 | Double charge + damaged item | refund, apologize, investigate, escalate |
| hard_3 | Premium subscription downgraded | restore, apologize, compensation, escalate |

## Grading System

### Programmatic Grading
- **Easy**: Exact category match (0 or 1.0)
- **Medium**: Order ID match (0.5) + Sentiment match (0.5)
- **Hard**: Keyword coverage ratio + step bonus

### LLM Grading (Optional)
For hard tasks, an optional LLM grader uses Meta Llama to evaluate response quality on:
- Empathy and tone (20%)
- Correctness of solution (40%)
- Completeness and actionability (20%)
- Professionalism (20%)

When enabled, the final score blends 60% programmatic + 40% LLM.

## Setup & Usage

### Prerequisites
- Docker (for containerized execution)
- Python 3.10+
- Hugging Face Token (set as `HF_TOKEN`) — Get from [hf.co/settings/tokens](https://huggingface.co/settings/tokens)

### Running with Docker
```bash
docker build -t supportautoenv .
docker run -e HF_TOKEN=your_hf_token -p 8000:8000 supportautoenv
```

### Running Manually
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn[standard] pydantic huggingface_hub websockets
   ```
2. Start the server:
   ```bash
   python server.py
   ```
3. Run baseline inference:
   ```bash
   export HF_TOKEN="your_huggingface_token"
   python inference.py
   ```

## API Endpoints

### REST API
| Method | Endpoint | Description |
|:---|:---|:---|
| GET | `/` | Health check + task list |
| POST | `/reset` | Reset environment, get first observation |
| POST | `/step` | Send action, get reward |
| GET | `/state` | Get current environment state |

### WebSocket API
| Endpoint | Description |
|:---|:---|
| WS `/ws` | Persistent session with isolated environment |

WebSocket protocol:
```json
// Send
{"action": "reset"}
{"action": "step", "payload": {"classification": "Billing"}}
{"action": "state"}

// Receive
{"type": "observation", "data": {...}}
{"type": "step_result", "observation": {...}, "reward": {...}, "done": true, "info": {...}}
{"type": "state", "data": {...}}
```

## Baseline Performance Scores

| Task | Score (0.0 - 1.0) |
| :--- | :--- |
| Easy (Classification) ×3 | 1.0 |
| Medium (Extraction) ×3 | 1.0 |
| Hard (Resolution) ×3 | ~0.85 |
| **Combined Average** | **~0.95** |

*Baseline generated using Meta Llama-3.1-8B-Instruct via HuggingFace Inference API.*

## Compliance
This environment complies with the OpenEnv interface specification.

## Project Structure
```text
.
├── server.py       # FastAPI + WebSocket server
├── env.py          # Environment logic (reset/step/state)
├── models.py       # Pydantic interfaces (Observation/Action/Reward)
├── graders.py      # Task definitions, programmatic + LLM grading
├── inference.py    # Baseline agent (Meta Llama via HuggingFace)
├── openenv.yaml    # OpenEnv metadata
├── Dockerfile      # Container deployment config
├── index.html      # Frontend dashboard
├── app.js          # Frontend logic
└── style.css       # Frontend styles
```

## Tech Stack
- **Backend**: Python, FastAPI, Pydantic
- **AI Model**: Meta Llama-3.1-8B-Instruct (via HuggingFace Inference API)
- **Protocol**: REST + WebSocket (OpenEnv standard)
- **Deployment**: Docker, Hugging Face Spaces
