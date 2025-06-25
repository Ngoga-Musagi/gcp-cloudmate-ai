# """
# MIT License

# Copyright (c) 2024 Ngoga Alexis

# Architecture Agent using LiteLLM with PlantUML (C4) Diagram Output
# """

# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm

# # Architecture agent using GPT-4o and PlantUML C4 support
# root_agent = Agent(
#     name="architecture_agent",
#     model=LiteLlm("openai/gpt-4o"),
#     description="An expert cloud architect that outputs production-ready system designs with PlantUML-based architecture diagrams including GCP service icons.",
#     instruction=(
#         "You are a world-class Google Cloud Platform system architect with 15+ years of experience designing "
#         "scalable, secure, and cost-optimized systems. You generate architecture diagrams using **PlantUML C4 model** "
#         "so they can be rendered visually with icons.\n\n"

#         "**YOUR TASK:** When given a system description:\n"
#         "1. Analyze the functional, non-functional, and technical requirements.\n"
#         "2. Design an enterprise-grade architecture using GCP services.\n"
#         "3. Generate a **PlantUML** diagram using the C4 model syntax, such as `Container(...)`, `System(...)`, and `Rel(...)`\n"
#         "4. Use `@startuml` and `@enduml` around your diagram. Always include this in your output:\n"
#         "   `!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml`\n"
#         "   This ensures icons and styling render properly.\n\n"

#         "**EXAMPLE PlantUML OUTPUT:**\n"
#         "```plantuml\n"
#         "@startuml\n"
#         "!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\n"
#         "Person(user, \"User\")\n"
#         "System_Boundary(webapp, \"Web App System\") {\n"
#         "  Container(lb, \"Cloud Load Balancer\", \"GCP\", \"Distributes incoming traffic\")\n"
#         "  Container(app, \"Cloud Run\", \"GCP\", \"Runs stateless microservices\")\n"
#         "  Container(db, \"Cloud SQL\", \"GCP\", \"Stores user and app data\")\n"
#         "}\n"
#         "Rel(user, lb, \"HTTPS\")\n"
#         "Rel(lb, app, \"HTTP\")\n"
#         "Rel(app, db, \"JDBC\")\n"
#         "@enduml\n"
#         "```\n\n"

#         "**FINAL OUTPUT FORMAT:**\n"
#         "```markdown\n"
#         "# System Architecture Solution\n"
#         "## Requirements Analysis\n"
#         "[Detailed analysis]\n\n"
#         "## Architecture Overview\n"
#         "[Pattern, complexity, estimated cost, deployment time]\n\n"
#         "## System Architecture\n"
#         "### Presentation Layer\n[Frontend services and components]\n"
#         "### Application Layer\n[Microservices and backend logic]\n"
#         "### Data Layer\n[Databases, storage]\n"
#         "### Security & Monitoring\n[Security, observability, compliance]\n\n"
#         "## Visual Architecture Diagram\n"
#         "```plantuml\n"
#         "[Full C4 PlantUML diagram here]\n"
#         "```\n\n"
#         "## Technical Specifications\n[Detailed configurations]\n"
#         "## Cost Analysis\n[Estimates + optimization suggestions]\n"
#         "## Implementation Roadmap\n[Phase-by-phase plan]\n"
#         "```\n\n"

#         "**STANDARDS:**\n"
#         "• Use valid PlantUML syntax\n"
#         "• Don't use emojis or unsupported characters\n"
#         "• Use proper service names and explain their roles\n"
#         "• Keep all content clear, technical, and actionable"
#     ),
#     tools=[]
# )

# """
# MIT License

# Copyright (c) 2024 Ngoga Alexis

# Architecture Agent using LiteLLM with PlantUML (C4) Diagram Output
# """

# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# import uuid
# import json

# # Define the agent
# root_agent = Agent(
#     name="architecture_agent",
#     model=LiteLlm("openai/gpt-4o"),  # Can switch to Claude or Gemini if needed
#     description="Expert cloud architect that generates system designs using PlantUML C4 model with GCP service recommendations.",
#     instruction=(
#         "You are a world-class Google Cloud Platform system architect with 15+ years of experience designing "
#         "scalable, secure, and cost-optimized systems. You generate architecture diagrams using **PlantUML C4 model** "
#         "so they can be rendered visually with icons.\n\n"

#         "**YOUR TASK:** When given a system description:\n"
#         "1. Analyze the functional, non-functional, and technical requirements.\n"
#         "2. Design an enterprise-grade architecture using GCP services.\n"
#         "3. Generate a **PlantUML** diagram using the C4 model syntax, such as `Container(...)`, `System(...)`, and `Rel(...)`\n"
#         "4. Use `@startuml` and `@enduml` around your diagram. Always include this in your output:\n"
#         "   `!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml`\n"
#         "   This ensures icons and styling render properly.\n\n"

#         "**FINAL OUTPUT FORMAT:**\n"
#         "```markdown\n"
#         "# System Architecture Solution\n"
#         "## Requirements Analysis\n"
#         "[Detailed analysis]\n\n"
#         "## Architecture Overview\n"
#         "[Pattern, complexity, estimated cost, deployment time]\n\n"
#         "## System Architecture\n"
#         "### Presentation Layer\n[Frontend services and components]\n"
#         "### Application Layer\n[Microservices and backend logic]\n"
#         "### Data Layer\n[Databases, storage]\n"
#         "### Security & Monitoring\n[Security, observability, compliance]\n\n"
#         "## Visual Architecture Diagram\n"
#         "```plantuml\n"
#         "[Full C4 PlantUML diagram here]\n"
#         "```\n\n"
#         "## Technical Specifications\n[Detailed configurations]\n"
#         "## Cost Analysis\n[Estimates + optimization suggestions]\n"
#         "## Implementation Roadmap\n[Phase-by-phase plan]\n"
#         "```\n\n"

#         "**STANDARDS:**\n"
#         "• Use valid PlantUML syntax\n"
#         "• Don't use emojis or unsupported characters\n"
#         "• Use proper service names and explain their roles\n"
#         "• Keep all content clear, technical, and actionable"
#     ),
#     tools=[]
# )

# # Session and runner
# session_service = InMemorySessionService()
# runner = Runner(
#     agent=root_agent,
#     app_name="architecture_app",
#     session_service=session_service
# )

# USER_ID = "user_architecture"

# # Execute method
# async def execute(request):
#     try:
#         if "prompt" not in request:
#             return {"status": "error", "error_message": "Missing 'prompt' in request."}

#         session_id = f"session_{uuid.uuid4().hex[:8]}"

#         await session_service.create_session(
#             app_name="architecture_app",
#             user_id=USER_ID,
#             session_id=session_id
#         )

#         message = types.Content(role="user", parts=[types.Part(text=request["prompt"])])

#         final_response = None
#         async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=message):
#             if event.is_final_response():
#                 final_response = event.content.parts[0].text
#                 break

#         try:
#             await session_service.delete_session(
#                 app_name="architecture_app",
#                 user_id=USER_ID,
#                 session_id=session_id
#             )
#         except:
#             pass

#         if final_response:
#             try:
#                 parsed = json.loads(final_response)
#                 return parsed if isinstance(parsed, dict) else {"response": final_response}
#             except json.JSONDecodeError:
#                 return {"response": final_response}
#         else:
#             return {"status": "error", "error_message": "No final response received"}

#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}

"""
MIT License

Copyright (c) 2024 Ngoga Alexis

Architecture Agent using LiteLLM with PlantUML (C4) Diagram Output
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import uuid
import json

# Define the agent
root_agent = Agent(
    name="architecture_agent",
    model=LiteLlm("openai/gpt-4o"),  # Can switch to Claude or Gemini if needed
    description="Expert cloud architect that generates system designs using PlantUML C4 model with GCP service recommendations.",
    instruction=(
        "You are a world-class Google Cloud Platform system architect with 15+ years of experience designing "
        "scalable, secure, and cost-optimized systems. You generate architecture diagrams using **PlantUML C4 model** "
        "so they can be rendered visually with icons.\n\n"

        "**YOUR TASK:** When given a system description:\n"
        "1. Analyze the functional, non-functional, and technical requirements.\n"
        "2. Design an enterprise-grade architecture using GCP services.\n"
        "3. Generate a **PlantUML** diagram using the C4 model syntax, such as `Container(...)`, `System(...)`, and `Rel(...)`\n"
        "4. Use `@startuml` and `@enduml` around your diagram. Always include this in your output:\n"
        "   `!includeurl https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml`\n"
        "   This ensures icons and styling render properly.\n\n"

        "**FINAL OUTPUT FORMAT:**\n"
        "```markdown\n"
        "# System Architecture Solution\n"
        "## Requirements Analysis\n"
        "[Detailed analysis]\n\n"
        "## Architecture Overview\n"
        "[Pattern, complexity, estimated cost, deployment time]\n\n"
        "## System Architecture\n"
        "### Presentation Layer\n[Frontend services and components]\n"
        "### Application Layer\n[Microservices and backend logic]\n"
        "### Data Layer\n[Databases, storage]\n"
        "### Security & Monitoring\n[Security, observability, compliance]\n\n"
        "## Visual Architecture Diagram\n"
        "```plantuml\n"
        "[Full C4 PlantUML diagram here]\n"
        "```\n\n"
        "## Technical Specifications\n[Detailed configurations]\n"
        "## Cost Analysis\n[Estimates + optimization suggestions]\n"
        "## Implementation Roadmap\n[Phase-by-phase plan]\n"
        "```\n\n"

        "**STANDARDS:**\n"
        "• Use valid PlantUML syntax\n"
        "• Don't use emojis or unsupported characters\n"
        "• Use proper service names and explain their roles\n"
        "• Keep all content clear, technical, and actionable"
    ),
    tools=[]
)

# Session and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="architecture_app",
    session_service=session_service
)

USER_ID = "user_architecture"

# Execute method
async def execute(request):
    try:
        if "prompt" not in request:
            return {"status": "error", "error_message": "Missing 'prompt' in request."}

        # CHANGED: Use provided session_id or create persistent one per user
        session_id = request.get("session_id", f"persistent_session_{USER_ID}")

        # CHANGED: Only create session if it doesn't already exist
        try:
            await session_service.create_session(
                app_name="architecture_app",
                user_id=USER_ID,
                session_id=session_id
            )
        except Exception:
            # Session likely already exists, which is fine
            pass

        message = types.Content(role="user", parts=[types.Part(text=request["prompt"])])

        final_response = None
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=message):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break

        # CHANGED: Don't delete session - keep it alive for follow-up conversations
        if request.get("end_conversation", False):
            try:
                await session_service.delete_session(
                    app_name="architecture_app",
                    user_id=USER_ID,
                    session_id=session_id
                )
            except:
                pass

        if final_response:
            try:
                parsed = json.loads(final_response)
                # ADDED: Add session_id to response for continuity
                if isinstance(parsed, dict):
                    parsed["session_id"] = session_id
                    return parsed
                else:
                    return {"response": final_response, "session_id": session_id}
            except json.JSONDecodeError:
                return {"response": final_response, "session_id": session_id}
        else:
            return {"status": "error", "error_message": "No final response received", "session_id": session_id}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}
