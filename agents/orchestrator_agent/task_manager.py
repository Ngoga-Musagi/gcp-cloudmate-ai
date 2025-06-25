# orchestrator_agent/task_manager.py

import json
import asyncio
import os
import httpx
import time
from common.a2a_client import call_agent
from typing import Dict, Optional


# Add this at the top (replace your existing URLs)
GCP_ADVISOR_URL = os.getenv("GCP_ADVISOR_URL", "http://localhost:8002/run")
ARCHITECTURE_URL = os.getenv("ARCHITECTURE_URL", "http://localhost:8003/run")
GCP_MANAGEMENT_URL = os.getenv("GCP_MANAGEMENT_URL", "http://localhost:8004/run")

AGENT_ENDPOINTS = {
    "gcp_advisor_agent": GCP_ADVISOR_URL,
    "architecture_agent": ARCHITECTURE_URL,
    "gcp_management_agent": GCP_MANAGEMENT_URL
}
# In-memory session storage (use Redis/database in production)
active_sessions: Dict[str, Dict] = {}

def get_session_id(payload: dict) -> str:
    """Extract or generate session ID"""
    # Try to get session ID from payload
    session_id = payload.get("session_id")
    if not session_id:
        # Fallback: use user_id or create default
        session_id = payload.get("user_id", "default_session")
    return session_id

def get_session_context(session_id: str) -> Optional[Dict]:
    """Get existing session context"""
    return active_sessions.get(session_id)

def update_session_context(session_id: str, context: Dict):
    """Update session context"""
    active_sessions[session_id] = context
    print(f"📝 Updated session {session_id}: {context}")

def clear_session(session_id: str):
    """Clear session when task is complete"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        print(f"🗑️ Cleared session {session_id}")

def analyze_conversation_context_simple(prompt: str, session_context: Optional[Dict]) -> Dict:
    """Simple rule-based conversation analysis (no LLM needed)"""
    
    if not session_context:
        # No session context - this is a new task
        return {
            "is_continuation": False,
            "active_agent": None,
            "task_status": "new_task",
            "primary_intent": "New request",
            "recommended_agent": classify_new_request_simple(prompt),
            "context_update": None
        }
    
    # Check if this looks like a continuation
    active_agent = session_context.get("active_agent")
    last_prompt = session_context.get("last_prompt", "").lower()
    current_prompt = prompt.lower()
    
    # Simple heuristics for continuation
    is_continuation = False
    
    if active_agent == "gcp_management_agent":
        # Check if user is providing requested information
        continuation_patterns = [
            "name is", "bucket name", "location", "region", "storage class",
            "yes", "no", "true", "false", "enable", "disable"
        ]
        if any(pattern in current_prompt for pattern in continuation_patterns):
            is_continuation = True
    
    elif active_agent == "architecture_agent":
        # Architecture follow-ups
        continuation_patterns = [
            "budget", "scale", "users", "data size", "requirements",
            "yes", "no", "more details", "explain"
        ]
        if any(pattern in current_prompt for pattern in continuation_patterns):
            is_continuation = True
    
    elif active_agent == "gcp_advisor_agent":
        # Advisor follow-ups
        continuation_patterns = [
            "budget", "cost", "scale", "more info", "details",
            "yes", "no", "what about", "compare"
        ]
        if any(pattern in current_prompt for pattern in continuation_patterns):
            is_continuation = True
    
    # Check for explicit new task keywords
    new_task_keywords = [
        "create", "delete", "design", "recommend", "help me with",
        "i want to", "can you", "new"
    ]
    
    if any(keyword in current_prompt for keyword in new_task_keywords):
        # This looks like a new task
        is_continuation = False
    
    return {
        "is_continuation": is_continuation,
        "active_agent": active_agent if is_continuation else None,
        "task_status": "in_progress" if is_continuation else "new_task",
        "primary_intent": "Continuation" if is_continuation else "New request",
        "recommended_agent": active_agent if is_continuation else classify_new_request_simple(prompt),
        "context_update": None
    }

def classify_new_request_simple(prompt: str) -> str:
    """Simple classification for brand new requests"""
    prompt_lower = prompt.lower()
    
    # Management keywords (highest priority)
    management_keywords = [
        "create", "delete", "make", "set up", "deploy", "configure", 
        "manage", "bucket", "database", "firestore", "instance"
    ]
    
    # Architecture keywords
    architecture_keywords = [
        "design", "architecture", "architect", "diagram", "pattern",
        "structure", "scalability", "system design", "blueprint"
    ]
    
    # Check for management first
    if any(word in prompt_lower for word in management_keywords):
        return "gcp_management_agent"
    
    # Check for architecture
    if any(word in prompt_lower for word in architecture_keywords):
        return "architecture_agent"
    
    # Default to advisor
    return "gcp_advisor_agent"

async def determine_agent_with_context(prompt: str, session_context: Optional[Dict]) -> tuple:
    """Determine which agent to use considering conversation context"""
    
    # Analyze conversation context using simple rules
    analysis = analyze_conversation_context_simple(prompt, session_context)
    
    print(f"🧠 Conversation analysis: {analysis}")
    
    # If this is a continuation, use the active agent
    if analysis.get("is_continuation") and session_context:
        active_agent = session_context.get("active_agent")
        if active_agent and active_agent in AGENT_ENDPOINTS:
            print(f"🔄 Continuing with {active_agent} (task in progress)")
            return active_agent, analysis
    
    # For new tasks, use the recommended agent
    recommended_agent = analysis.get("recommended_agent", "gcp_advisor_agent")
    print(f"🆕 New task detected, assigned to {recommended_agent}")
    return recommended_agent, analysis

async def call_agent_with_retry(url: str, payload: dict, max_retries: int = 3) -> dict:
    """Call agent with retry logic - simplified version"""
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries} calling {url}")
            
            # Direct call to agent - no health check needed
            response = await call_agent(url, payload)
            print(f"✅ Successfully called {url}")
            return response
            
        except Exception as e:
            last_error = e
            print(f"❌ Attempt {attempt + 1} failed: {str(e)[:100]}...")
            
            if attempt < max_retries - 1:
                wait_time = 1  # Simple 1 second wait between retries
                print(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
    
    # If all retries failed
    return {
        "error": f"Failed to call agent after {max_retries} attempts. Last error: {str(last_error)[:100]}",
        "connection_failed": True,
        "url": url
    }

async def run(payload):
    prompt = payload.get("prompt", "")
    session_id = get_session_id(payload)
    
    print(f"🚀 Orchestrator received prompt: '{prompt}' (session: {session_id})")
    
    # Get existing session context
    session_context = get_session_context(session_id)
    print(f"📋 Session context: {session_context}")
    
    # Determine which agent to use
    agent_to_call, analysis = await determine_agent_with_context(prompt, session_context)
    
    # FIXED: Handle None session_context properly
    conversation_history = []
    if session_context and "conversation_history" in session_context:
        conversation_history = session_context["conversation_history"]
    
    # Update session context
    new_context = {
        "active_agent": agent_to_call,
        "last_prompt": prompt,
        "task_status": analysis.get("task_status", "in_progress"),
        "conversation_history": conversation_history + [
            {"user": prompt, "agent_called": agent_to_call}
        ]
    }
    
    # Add any context updates from analysis
    if analysis.get("context_update"):
        new_context.update(analysis["context_update"])
    
    update_session_context(session_id, new_context)
    
    print(f"🎯 Selected agent: {agent_to_call}")
    
    # Get agent URL
    url = AGENT_ENDPOINTS.get(agent_to_call)
    if not url:
        return {"status": "error", "error": f"Unknown agent: {agent_to_call}"}
    
    print(f"📡 Sending payload to {agent_to_call} at {url}")
    
    # Add session context to payload for the agent
    enhanced_payload = payload.copy()
    enhanced_payload["session_context"] = session_context
    enhanced_payload["session_id"] = session_id
    
    # Call the agent with retry logic
    response = await call_agent_with_retry(url, enhanced_payload)
    
    # Check if there was a connection error
    if "connection_failed" in response:
        print(f"❌ Failed to connect to {agent_to_call}")
        return {
            "status": "error",
            "agent_called": agent_to_call,
            "session_id": session_id,
            "error": response.get("error"),
            "suggested_action": f"Please ensure {agent_to_call} is running on {url}",
            "results": {agent_to_call: response}
        }
    
    print(f"✅ Response from {agent_to_call}: Success")
    
    # Check if task is completed (you can enhance this logic)
    if is_task_completed(response, analysis):
        clear_session(session_id)
        print("✅ Task completed, session cleared")
    
    return {
        "status": "success",
        "agent_called": agent_to_call,
        "session_id": session_id,
        "is_continuation": analysis.get("is_continuation", False),
        "results": {agent_to_call: response}
    }

def is_task_completed(response: dict, analysis: dict) -> bool:
    """Determine if the task is completed based on agent response"""
    # Simple heuristic - you can make this more sophisticated
    response_text = str(response).lower()
    
    # Check for completion indicators
    completion_indicators = [
        "bucket created successfully",
        "task completed",
        "successfully created",
        "deployment complete"
    ]
    
    return any(indicator in response_text for indicator in completion_indicators)

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