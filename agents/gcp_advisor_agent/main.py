"""
MIT License

Copyright (c) 2024 Ngoga Alexis

This is an educational example demonstrating how to integrate Google ADK with Chainlit.
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
from agent import root_agent
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Set up session service and runner
session_service = InMemorySessionService()
APP_NAME = "gcp_advisor_app"
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    # Create a new session for each chat
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id="chainlit_user",
        session_id=cl.user_session.get("session_id", "session_001")
    )
    cl.user_session.set("session_id", session.id)
    
    # Send welcome message
    await cl.Message(
        content="👋 Hi! I'm your GCP Advisor. I can help you choose the right Google Cloud Platform services "
                "based on your use case, budget, and requirements. What would you like to build?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    try:
        # Create content from the message
        content = types.Content(role='user', parts=[types.Part(text=message.content)])
        
        # Get the session ID
        session_id = cl.user_session.get("session_id")
        
        # Process the message through the ADK agent using the runner
        # Run in executor since runner.run() is synchronous
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(
            None,
            lambda: runner.run(
                user_id="chainlit_user",
                session_id=session_id,
                new_message=content
            )
        )
        
        # Process each event from the generator
        for event in events:
            if event.is_final_response():
                # Extract the text content from the event
                response_text = ""
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        for part in event.content.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text
                    elif isinstance(event.content, str):
                        response_text = event.content
                
                if response_text:
                    await cl.Message(content=response_text).send()
                else:
                    await cl.Message(content="I received a response but couldn't extract the text content.").send()
            
    except Exception as e:
        await cl.Message(
            content=f"An error occurred: {str(e)}\nTrace: {type(e).__name__}"
        ).send()