"""
MIT License

Copyright (c) 2024 Ngoga Alexis

This is an educational example demonstrating how to integrate multi-agent orchestrator with Chainlit.
Feel free to use, modify, and share this code for learning purposes.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so.

See the LICENSE file for the full license text.
"""

import chainlit as cl
import requests
import json
import time
import os

# Configuration
# ORCHESTRATOR_ENDPOINT = "http://localhost:8001/run"
# Add this at the top
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8001/run")


# Track ongoing requests to prevent duplicates
ongoing_requests = set()

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    welcome_message = """
🧠 **Welcome to GCP Multi-Agent Assistant!**

I can help you with:
- 🏗️ **Architecture Design**: Design GCP architectures for your applications
- 💡 **GCP Service Advice**: Get recommendations for the best GCP services
- ⚙️ **Resource Management**: Create, manage, or delete GCP resources

**Examples of what you can ask:**
- "Recommend GCP services for a scalable e-commerce platform"
- "Design a GCP architecture for a video analytics pipeline"
- "Create a new storage bucket called 'my-app-data' in us-central1"
- "Delete a Firestore database named 'test-db'"

What would you like to do today?
    """
    
    await cl.Message(content=welcome_message).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    user_prompt = message.content.strip()
    
    if not user_prompt:
        await cl.Message(content="⚠️ Please provide a task or question for me to help you with.").send()
        return
    
    # Create a unique request ID to prevent duplicates
    request_id = f"{user_prompt}_{int(time.time() * 1000)}"
    
    # Check if this request is already being processed
    if request_id in ongoing_requests:
        return
    
    # Add to ongoing requests
    ongoing_requests.add(request_id)
    
    try:
        # Show typing indicator
        async with cl.Step(name="Processing", type="run") as step:
            step.output = "Coordinating with specialized agents..."
            
            # Prepare payload for orchestrator
            payload = {"prompt": user_prompt}
            
            # Make synchronous HTTP request to orchestrator endpoint
            response = requests.post(
                ORCHESTRATOR_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # 60 second timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", {})
                
                if not results:
                    await cl.Message(content="No responses received from agents.").send()
                else:
                    # Process results from each agent
                    response_parts = []
                    
                    for agent_name, agent_data in results.items():
                        if isinstance(agent_data, dict):
                            content = (
                                agent_data.get("response") or 
                                agent_data.get("error") or 
                                str(agent_data)
                            )
                        else:
                            content = str(agent_data)
                        
                        response_parts.append(f"## {agent_name}\n\n{content}")
                    
                    # Send combined response
                    final_response = "\n\n---\n\n".join(response_parts)
                    await cl.Message(content=final_response).send()
            
            else:
                error_msg = f"Agent call failed with status {response.status_code}. Please check that the backend is running."
                await cl.Message(content=error_msg).send()
    
    except requests.exceptions.Timeout:
        await cl.Message(content="Request timed out. The orchestrator is taking too long to respond.").send()
    
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {str(e)}\n\nPlease ensure the orchestrator backend is running on {ORCHESTRATOR_ENDPOINT}"
        await cl.Message(content=error_msg).send()
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        await cl.Message(content=error_msg).send()
    
    except json.JSONDecodeError as e:
        error_msg = f"Invalid response format from orchestrator: {str(e)}"
        await cl.Message(content=error_msg).send()
    
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        await cl.Message(content=error_msg).send()
    
    finally:
        # Always remove from ongoing requests when done
        ongoing_requests.discard(request_id)
