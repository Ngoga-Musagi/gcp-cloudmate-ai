# gcp_advisor_agent/task_manager.py

from .agent import execute

async def run(payload):
    return await execute(payload)
