# orchestrator_agent/__main__.py

from common.a2a_server import create_app
from .task_manager import run

# Create the FastAPI app and bind the orchestrator's run function
app = create_app(agent=type("Agent", (), {"execute": run}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Orchestrator typically runs on base port
