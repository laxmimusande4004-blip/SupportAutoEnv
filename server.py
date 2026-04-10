import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from models import SupportAction, SupportObservation, SupportReward
from env import SupportEnv
from typing import Any, Dict

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SupportAutoEnv API",
    description="Customer Support Automation Environment — OpenEnv Standard Compliant",
    version="0.2.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SupportEnv()

# ============================================================
# REST Endpoints (standard OpenEnv interface)
# ============================================================

@app.get("/")
async def root():
    """Serve the frontend dashboard when visiting the root URL."""
    return FileResponse("index.html")

@app.get("/api")
async def api_info():
    """API info endpoint for programmatic access."""
    from graders import TASKS
    return {
        "message": "SupportAutoEnv is running",
        "version": "0.2.0",
        "spec": "OpenEnv v1",
        "tasks": [t["id"] for t in TASKS]
    }

@app.post("/reset")
async def reset() -> SupportObservation:
    try:
        obs = env.reset()
        return obs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(action: SupportAction) -> Dict[str, Any]:
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs,
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_state() -> Dict[str, Any]:
    return {"state": env.state()}

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="."), name="static")

# Serve app.js and style.css directly
@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

@app.get("/style.css")
async def serve_css():
    return FileResponse("style.css")

# ============================================================
# WebSocket Endpoint (OpenEnv persistent session support)
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for persistent environment sessions.
    Each connection gets its own isolated environment instance.
    
    Protocol:
      Send JSON: {"action": "reset"} | {"action": "step", "payload": {...}} | {"action": "state"}
      Receive JSON: response with type field
    """
    await websocket.accept()
    ws_env = SupportEnv()  # Isolated env per WebSocket connection

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            action_type = data.get("action", "")

            if action_type == "reset":
                obs = ws_env.reset()
                await websocket.send_json({
                    "type": "observation",
                    "data": obs.model_dump()
                })

            elif action_type == "step":
                payload = data.get("payload", {})
                action = SupportAction(**payload)
                obs, reward, done, info = ws_env.step(action)
                await websocket.send_json({
                    "type": "step_result",
                    "observation": obs.model_dump(),
                    "reward": reward.model_dump(),
                    "done": done,
                    "info": info
                })

            elif action_type == "state":
                await websocket.send_json({
                    "type": "state",
                    "data": ws_env.state()
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action_type}. Use 'reset', 'step', or 'state'."
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
