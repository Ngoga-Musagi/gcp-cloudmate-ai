# orchestrator_agent/task_manager.py

import json
import asyncio
import os
import httpx
from typing import Dict, Optional

from common.a2a_client import call_agent
from litellm import completion

# Default to local URLs, but can be overridden by environment variables for cloud
GCP_ADVISOR_URL = os.getenv("GCP_ADVISOR_URL", "http://localhost:8002/run")
ARCHITECTURE_URL = os.getenv("ARCHITECTURE_URL", "http://localhost:8003/run")
GCP_MANAGEMENT_URL = os.getenv("GCP_MANAGEMENT_URL", "http://localhost:8004/run")

# a2a_client = A2AClient()

AGENT_ENDPOINTS = {
    "gcp_advisor_agent": GCP_ADVISOR_URL,
    "architecture_agent": ARCHITECTURE_URL,
    "gcp_management_agent": GCP_MANAGEMENT_URL
}

# In-memory session storage (use Redis or another persistent store in production)
active_sessions: Dict[str, Dict] = {}


def get_session_id(payload: dict) -> str:
    """Extracts or generates a session ID from the payload."""
    return payload.get("session_id", payload.get("user_id", "default_session"))


def get_session_context(session_id: str) -> Optional[Dict]:
    """Retrieves the context for a given session ID."""
    return active_sessions.get(session_id)


def update_session_context(session_id: str, context: Dict):
    """Updates the context for a given session ID."""
    active_sessions[session_id] = context
    print(f"📝 Updated session {session_id}: {context}")


def clear_session(session_id: str):
    """Clears a session once a task is complete."""
    if session_id in active_sessions:
        del active_sessions[session_id]
        print(f"🗑️ Cleared session {session_id}")


def classify_new_request_with_llm(prompt: str) -> str:
    """Uses an LLM to classify a new request and recommend an agent."""
    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a classification expert for a multi-agent system. "
                        "Your task is to recommend the best agent for a given user prompt. "
                        "The available agents are: "
                        "1. 'gcp_advisor_agent': Recommends GCP services and provides advice. "
                        "2. 'architecture_agent': Designs system architectures and diagrams. "
                        "3. 'gcp_management_agent': Manages GCP resources (creates, deletes, etc.). "
                        "Respond with only the agent's name (e.g., 'gcp_management_agent')."
                    ),
                },
                {"role": "user", "content": f"Prompt: '{prompt}'"},
            ],
            temperature=0.0,
        )
        recommended_agent = response.choices[0].message.content.strip()
        if recommended_agent in AGENT_ENDPOINTS:
            return recommended_agent
    except Exception as e:
        print(f"Error during LLM classification: {e}")
    # Fallback to simple classification
    return classify_new_request_simple(prompt)


def classify_new_request_simple(prompt: str) -> str:
    """A simple keyword-based classifier for new requests."""
    prompt_lower = prompt.lower()
    management_keywords = ["create", "delete", "make", "deploy", "configure", "bucket", "database", "instance"]
    architecture_keywords = ["design", "architecture", "diagram", "pattern", "structure"]

    if any(word in prompt_lower for word in management_keywords):
        return "gcp_management_agent"
    if any(word in prompt_lower for word in architecture_keywords):
        return "architecture_agent"
    return "gcp_advisor_agent"


async def determine_agent(prompt: str, session_context: Optional[Dict]) -> str:
    """Determines which agent to use based on conversation context or LLM classification."""
    if session_context and session_context.get("active_agent"):
        # Simple check if the user is continuing the conversation
        # A more advanced check could analyze the prompt for continuation cues
        if "last_prompt" in session_context:
             return session_context["active_agent"]

    # For new tasks, classify the prompt
    return classify_new_request_with_llm(prompt)


async def run(payload: dict):
    """Main entry point for the orchestrator task manager."""
    prompt = payload.get("prompt", "")
    session_id = get_session_id(payload)
    session_context = get_session_context(session_id)

    print(f"🚀 Orchestrator received prompt: '{prompt}' (session: {session_id})")

    agent_to_call = await determine_agent(prompt, session_context)
    print(f"🎯 Selected agent: {agent_to_call}")

    url = AGENT_ENDPOINTS.get(agent_to_call)
    if not url or url == "not-set-in-cloud":
        return {"status": "error", "message": f"Agent '{agent_to_call}' is not configured or its URL is not set."}

    # Prepare the payload for the target agent
    agent_payload = payload.copy()
    agent_payload["session_context"] = session_context

    # Call the selected agent
    response = await call_agent(url, agent_payload)

    # Update the session context
    new_context = {
        "active_agent": agent_to_call,
        "last_prompt": prompt,
        "conversation_history": (session_context.get("conversation_history", []) if session_context else []) + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response.get("message", "")}
        ],
    }
    update_session_context(session_id, new_context)
    
    # Check if the task is complete (this is a simplified check)
    if response.get("task_status") == "completed":
        clear_session(session_id)
        print("✅ Task completed, session cleared.")

    return {
        "status": "success",
        "agent_called": agent_to_call,
        "session_id": session_id,
        "results": response,
    }

# REMOVED: Health check functions since we only need /run endpoints

# ADDED: Simple health check for debugging (optional)
async def check_all_agents_health():
    """Check health of all agents by testing /run endpoint - useful for debugging"""
    health_status = {}
    
    for agent_name, url in AGENT_ENDPOINTS.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json={"prompt": "health_check"})
                is_healthy = response.status_code in [200, 422]
        except Exception as e:
            is_healthy = False
            
        health_status[agent_name] = {
            "url": url,
            "healthy": is_healthy,
            "status": "✅ Online" if is_healthy else "❌ Offline"
        }
        print(f"{health_status[agent_name]['status']} {agent_name} ({url})")
    
    return health_status