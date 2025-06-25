# gcp_management_agent/__main__.py

from common.a2a_server import create_app
from .agent import execute

# Create a FastAPI app exposing the /run endpoint
app = create_app(agent=type("Agent", (), {"execute": execute}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
