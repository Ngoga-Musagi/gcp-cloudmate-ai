# # # orchestrator_agent/agent.py

# # # orchestrator_agent/agent.py

# # from google.adk.agents import Agent
# # from google.adk.models.lite_llm import LiteLlm
# # from google.adk.runners import Runner
# # from google.adk.sessions import InMemorySessionService
# # from google.genai import types

# # # Import the tools from task_manager

# # # Define the Orchestrator Agent
# # root_agent = Agent(
# #     name="orchestrator_agent",
# #     model=LiteLlm("openai/gpt-4o"),
# #     description="Routes GCP-related requests to appropriate tools.",
# #     instruction=(
# #         "You are an intelligent orchestrator that decides which specialized agent to invoke based on the user's goal.\n"
# #         "Call only the necessary tools:\n"
# #         "- gcp_advisor_agent for cost/compliance/service suggestions.\n"
# #         "- architecture_agent for system diagrams or design help.\n"
# #         "- gcp_management_agent for resource creation/deletion (buckets, Firestore).\n"
# #         "Provide a clean final summary to the user."
# #     ),
# #     tools=[]
# # )

# # # Runner setup
# # session_service = InMemorySessionService()
# # runner = Runner(
# #     agent=root_agent,
# #     app_name="orchestrator_app",
# #     session_service=session_service
# # )

# # USER_ID = "user_orchestrator"
# # SESSION_ID = "session_orchestrator"

# # # Handler function for execution
# # async def execute(request):
# #     try:
# #         prompt = request.get("prompt")
# #         if not prompt:
# #             return {"status": "error", "error_message": "Missing 'prompt' in request."}

# #         await session_service.create_session(
# #             app_name="orchestrator_app",
# #             user_id=USER_ID,
# #             session_id=SESSION_ID
# #         )

# #         message = types.Content(role="user", parts=[types.Part(text=prompt)])

# #         final_response = None
# #         async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
# #             if event.is_final_response():
# #                 final_response = event.content.parts[0].text
# #                 break

# #         await session_service.delete_session(
# #             app_name="orchestrator_app",
# #             user_id=USER_ID,
# #             session_id=SESSION_ID
# #         )

# #         return {"summary": final_response} if final_response else {"status": "error", "error_message": "No response from orchestrator"}

# #     except Exception as e:
# #         return {"status": "error", "error_message": str(e)}


# # orchestrator_agent/agent.py

# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# import uuid
# import json

# # Define the Orchestrator Agent
# root_agent = Agent(
#     name="orchestrator_agent",
#     # model=LiteLlm("openai/gpt-4o"),
#     model="gemini-1.5-flash",
#     description="Analyzes GCP-related requests to determine which specialized agent (singular or multiple) should handle them.",
#     instruction=(
#         "You are an intelligent orchestrator that analyzes user requests and determines which specialized agent(s) should handle them.\n\n"
#         "Available specialized agents:\n"
#         "- gcp_advisor_agent: Provides GCP service recommendations, cost estimates, compliance guidance, and helps choose between GCP services\n"
#         "- architecture_agent: Designs system architectures, creates diagrams, provides design patterns, scalability solutions, and system structure advice\n"
#         "- gcp_management_agent: Manages GCP resources like creating/deleting storage buckets, managing Firestore databases, and hands-on resource operations\n\n"
#         "Your task is to analyze the user's request and return ONLY a JSON array of agent names that should handle the request.\n\n"
#         "Guidelines:\n"
#         "- Many tasks can be completed by just ONE agent - don't add unnecessary agents\n"
#         "- If the user asks about costs, recommendations, or 'what service should I use' → ONLY gcp_advisor_agent\n"
#         "- If the user asks about architecture, design patterns, scalability → ONLY architecture_agent\n"
#         "- If the user asks about creating, managing, or configuring specific GCP resources → ONLY gcp_management_agent\n"
#         "- Only use MULTIPLE agents when the task genuinely requires different types of expertise\n"
#         "- Examples of multi-agent tasks: 'Design a cost-effective architecture', 'Create resources and optimize costs'\n"
#         "- Return ONLY a JSON array like [\"gcp_advisor_agent\"] or [\"architecture_agent\", \"gcp_advisor_agent\"] with no other text\n"
#         "- When in doubt, choose the SINGLE most relevant agent rather than multiple"
#     ),
#     tools=[]
# )

# # Setup session management and runner
# session_service = InMemorySessionService()
# runner = Runner(
#     agent=root_agent,
#     app_name="orchestrator_app",
#     session_service=session_service
# )

# USER_ID = "user_orchestrator"

# async def execute(request):
#     try:
#         if "prompt" not in request:
#             return {"status": "error", "error_message": "Missing 'prompt' in request."}

#         session_id = f"session_{uuid.uuid4().hex[:8]}"

#         await session_service.create_session(
#             app_name="orchestrator_app",
#             user_id=USER_ID,
#             session_id=session_id
#         )

#         # Wrap user prompt in a Content message
#         message = types.Content(role="user", parts=[types.Part(text=request["prompt"])])

#         final_response = None
#         async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=message):
#             if event.is_final_response():
#                 final_response = event.content.parts[0].text
#                 break

#         try:
#             await session_service.delete_session(
#                 app_name="orchestrator_app",
#                 user_id=USER_ID,
#                 session_id=session_id
#             )
#         except:
#             pass

#         if final_response:
#             try:
#                 # Try to parse as JSON array of agents
#                 agents = json.loads(final_response.strip())
#                 if isinstance(agents, list):
#                     return {"agents_to_call": agents}
#                 else:
#                     return {"agents_to_call": ["gcp_advisor_agent"], "note": "Invalid format, defaulting to advisor"}
#             except json.JSONDecodeError:
#                 # If not valid JSON, extract agent names from text
#                 agent_names = ["gcp_advisor_agent", "architecture_agent", "gcp_management_agent"]
#                 found_agents = [name for name in agent_names if name in final_response]
#                 if found_agents:
#                     return {"agents_to_call": found_agents}
#                 else:
#                     return {"agents_to_call": ["gcp_advisor_agent"], "note": "Could not parse agents, defaulting to advisor"}
#         else:
#             return {"agents_to_call": ["gcp_advisor_agent"], "error": "No response from orchestrator"}

#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}



# # orchestrator_agent/agent.py

# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# import uuid
# import json

# # Define the Orchestrator Agent
# root_agent = Agent(
#     name="orchestrator_agent",
#     model="gemini-1.5-flash",
#     description="Analyzes GCP-related requests to determine which specialized agent should handle them based on specific action keywords.",
#     instruction=(
#         "You are an intelligent orchestrator that analyzes user requests and determines which specialized agent should handle them.\n\n"
#         "Available specialized agents:\n"
#         "- gcp_advisor_agent: For service recommendations, cost estimates, compliance guidance, and choosing between GCP services\n"
#         "- architecture_agent: For designing system architectures, creating diagrams, design patterns, and system structure advice\n"
#         "- gcp_management_agent: For creating, deleting, or managing GCP resources (buckets, databases, etc.)\n\n"
#         "DECISION RULES (follow these exactly):\n\n"
#         "1. If the user wants to CREATE, DELETE, MANAGE, or CONFIGURE specific resources → gcp_management_agent\n"
#         "   Keywords: 'create', 'delete', 'make', 'set up', 'configure', 'manage', 'bucket', 'database'\n"
#         "   Examples: 'create a storage bucket', 'delete database', 'set up firestore'\n\n"
#         "2. If the user wants to DESIGN, ARCHITECT, or get DESIGN PATTERNS → architecture_agent\n"
#         "   Keywords: 'design', 'architecture', 'diagram', 'pattern', 'structure', 'scalability'\n"
#         "   Examples: 'design my system', 'architecture for my app', 'design patterns'\n\n"
#         "3. If the user wants RECOMMENDATIONS, ADVICE, or COST ESTIMATES → gcp_advisor_agent\n"
#         "   Keywords: 'recommend', 'suggest', 'which service', 'cost', 'budget', 'compare'\n"
#         "   Examples: 'recommend a service', 'what should I use', 'cost estimate'\n\n"
#         "IMPORTANT:\n"
#         "- Look for ACTION WORDS in the user's request\n"
#         "- If the user says 'create', 'make', 'set up' → always use gcp_management_agent\n"
#         "- If the user says 'design', 'architecture' → always use architecture_agent\n"
#         "- Return ONLY a JSON array with ONE agent name\n"
#         "- Examples: [\"gcp_management_agent\"] or [\"architecture_agent\"] or [\"gcp_advisor_agent\"]\n"
#         "- NO other text, just the JSON array\n"
#     ),
#     tools=[]
# )

# # Setup session management and runner
# session_service = InMemorySessionService()
# runner = Runner(
#     agent=root_agent,
#     app_name="orchestrator_app",
#     session_service=session_service
# )

# USER_ID = "user_orchestrator"

# async def execute(request):
#     try:
#         if "prompt" not in request:
#             return {"status": "error", "error_message": "Missing 'prompt' in request."}

#         session_id = f"session_{uuid.uuid4().hex[:8]}"

#         await session_service.create_session(
#             app_name="orchestrator_app",
#             user_id=USER_ID,
#             session_id=session_id
#         )

#         # Enhanced prompt with clear examples
#         user_prompt = request["prompt"]
#         enhanced_prompt = f"""
# Analyze this user request and determine which agent to call: "{user_prompt}"

# Remember:
# - Words like "create", "make", "set up", "delete" → gcp_management_agent
# - Words like "design", "architecture", "diagram" → architecture_agent  
# - Words like "recommend", "suggest", "which service" → gcp_advisor_agent

# Return only the JSON array with the agent name.
# """

#         message = types.Content(role="user", parts=[types.Part(text=enhanced_prompt)])

#         final_response = None
#         async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=message):
#             if event.is_final_response():
#                 final_response = event.content.parts[0].text
#                 break

#         try:
#             await session_service.delete_session(
#                 app_name="orchestrator_app",
#                 user_id=USER_ID,
#                 session_id=session_id
#             )
#         except:
#             pass

#         if final_response:
#             try:
#                 # Clean the response - remove any markdown formatting
#                 clean_response = final_response.strip()
#                 if clean_response.startswith("```json"):
#                     clean_response = clean_response.replace("```json", "").replace("```", "").strip()
                
#                 # Try to parse as JSON array of agents
#                 agents = json.loads(clean_response)
#                 if isinstance(agents, list) and len(agents) > 0:
#                     # Validate the agent name
#                     valid_agents = ["gcp_advisor_agent", "architecture_agent", "gcp_management_agent"]
#                     if agents[0] in valid_agents:
#                         return {"agents_to_call": agents}
                
#                 # Fallback logic based on keywords in original prompt
#                 prompt_lower = user_prompt.lower()
#                 if any(word in prompt_lower for word in ["create", "make", "set up", "delete", "bucket", "database", "manage"]):
#                     return {"agents_to_call": ["gcp_management_agent"], "note": "Fallback to management agent"}
#                 elif any(word in prompt_lower for word in ["design", "architecture", "diagram", "pattern"]):
#                     return {"agents_to_call": ["architecture_agent"], "note": "Fallback to architecture agent"}
#                 else:
#                     return {"agents_to_call": ["gcp_advisor_agent"], "note": "Fallback to advisor agent"}
                    
#             except json.JSONDecodeError:
#                 # Keyword-based fallback
#                 prompt_lower = user_prompt.lower()
#                 if any(word in prompt_lower for word in ["create", "make", "set up", "delete", "bucket", "database"]):
#                     return {"agents_to_call": ["gcp_management_agent"], "note": "Keyword-based routing"}
#                 elif any(word in prompt_lower for word in ["design", "architecture", "diagram"]):
#                     return {"agents_to_call": ["architecture_agent"], "note": "Keyword-based routing"}
#                 else:
#                     return {"agents_to_call": ["gcp_advisor_agent"], "note": "Default routing"}
#         else:
#             return {"agents_to_call": ["gcp_advisor_agent"], "error": "No response from orchestrator"}

#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}


from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import uuid
import json

# Define the Orchestrator Agent
root_agent = Agent(
    name="orchestrator_agent",
    model="gemini-1.5-flash",
    description="Analyzes GCP-related requests to determine which specialized agent should handle them based on specific action keywords.",
    instruction=(
        "You are an intelligent orchestrator that analyzes user requests and determines which specialized agent should handle them.\n\n"
        "Available specialized agents:\n"
        "- gcp_advisor_agent: For service recommendations, cost estimates, compliance guidance, and choosing between GCP services\n"
        "- architecture_agent: For designing system architectures, creating diagrams, design patterns, and system structure advice\n"
        "- gcp_management_agent: For creating, deleting, or managing GCP resources (buckets, databases, etc.)\n\n"
        "DECISION RULES (follow these exactly):\n\n"
        "1. If the user wants to CREATE, DELETE, MANAGE, or CONFIGURE specific resources → gcp_management_agent\n"
        "   Keywords: 'create', 'delete', 'make', 'set up', 'configure', 'manage', 'bucket', 'database'\n"
        "   Examples: 'create a storage bucket', 'delete database', 'set up firestore'\n\n"
        "2. If the user wants to DESIGN, ARCHITECT, or get DESIGN PATTERNS → architecture_agent\n"
        "   Keywords: 'design', 'architecture', 'diagram', 'pattern', 'structure', 'scalability'\n"
        "   Examples: 'design my system', 'architecture for my app', 'design patterns'\n\n"
        "3. If the user wants RECOMMENDATIONS, ADVICE, or COST ESTIMATES → gcp_advisor_agent\n"
        "   Keywords: 'recommend', 'suggest', 'which service', 'cost', 'budget', 'compare'\n"
        "   Examples: 'recommend a service', 'what should I use', 'cost estimate'\n\n"
        "IMPORTANT:\n"
        "- Look for ACTION WORDS in the user's request\n"
        "- If the user says 'create', 'make', 'set up' → always use gcp_management_agent\n"
        "- If the user says 'design', 'architecture' → always use architecture_agent\n"
        "- Return ONLY a JSON array with ONE agent name\n"
        "- Examples: [\"gcp_management_agent\"] or [\"architecture_agent\"] or [\"gcp_advisor_agent\"]\n"
        "- NO other text, just the JSON array\n"
    ),
    tools=[]
)

# Setup session management and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="orchestrator_app",
    session_service=session_service
)

USER_ID = "user_orchestrator"

async def execute(request):
    try:
        if "prompt" not in request:
            return {"status": "error", "error_message": "Missing 'prompt' in request."}

        # CHANGED: Use provided session_id or create persistent one per user
        session_id = request.get("session_id", f"persistent_session_{USER_ID}")
        
        # CHANGED: Only create session if it doesn't already exist
        try:
            await session_service.create_session(
                app_name="orchestrator_app",
                user_id=USER_ID,
                session_id=session_id
            )
        except Exception:
            # Session likely already exists, which is fine
            pass

        # Enhanced prompt with clear examples
        user_prompt = request["prompt"]
        enhanced_prompt = f"""
Analyze this user request and determine which agent to call: "{user_prompt}"

Remember:
- Words like "create", "make", "set up", "delete" → gcp_management_agent
- Words like "design", "architecture", "diagram" → architecture_agent  
- Words like "recommend", "suggest", "which service" → gcp_advisor_agent

Return only the JSON array with the agent name.
"""

        message = types.Content(role="user", parts=[types.Part(text=enhanced_prompt)])

        final_response = None
        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=message):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break

        # CHANGED: Don't delete session - keep it alive for follow-up conversations
        if request.get("end_conversation", False):
            try:
                await session_service.delete_session(
                    app_name="orchestrator_app",
                    user_id=USER_ID,
                    session_id=session_id
                )
            except:
                pass

        if final_response:
            try:
                # Clean the response - remove any markdown formatting
                clean_response = final_response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response.replace("```json", "").replace("```", "").strip()
                
                # Try to parse as JSON array of agents
                agents = json.loads(clean_response)
                if isinstance(agents, list) and len(agents) > 0:
                    # Validate the agent name
                    valid_agents = ["gcp_advisor_agent", "architecture_agent", "gcp_management_agent"]
                    if agents[0] in valid_agents:
                        return {
                            "agents_to_call": agents,
                            "session_id": session_id  # ADDED: Return session_id for next request
                        }
                
                # Fallback logic based on keywords in original prompt
                prompt_lower = user_prompt.lower()
                if any(word in prompt_lower for word in ["create", "make", "set up", "delete", "bucket", "database", "manage"]):
                    return {
                        "agents_to_call": ["gcp_management_agent"], 
                        "session_id": session_id,
                        "note": "Fallback to management agent"
                    }
                elif any(word in prompt_lower for word in ["design", "architecture", "diagram", "pattern"]):
                    return {
                        "agents_to_call": ["architecture_agent"], 
                        "session_id": session_id,
                        "note": "Fallback to architecture agent"
                    }
                else:
                    return {
                        "agents_to_call": ["gcp_advisor_agent"], 
                        "session_id": session_id,
                        "note": "Fallback to advisor agent"
                    }
                    
            except json.JSONDecodeError:
                # Keyword-based fallback
                prompt_lower = user_prompt.lower()
                if any(word in prompt_lower for word in ["create", "make", "set up", "delete", "bucket", "database"]):
                    return {
                        "agents_to_call": ["gcp_management_agent"], 
                        "session_id": session_id,
                        "note": "Keyword-based routing"
                    }
                elif any(word in prompt_lower for word in ["design", "architecture", "diagram"]):
                    return {
                        "agents_to_call": ["architecture_agent"], 
                        "session_id": session_id,
                        "note": "Keyword-based routing"
                    }
                else:
                    return {
                        "agents_to_call": ["gcp_advisor_agent"], 
                        "session_id": session_id,
                        "note": "Default routing"
                    }
        else:
            return {
                "agents_to_call": ["gcp_advisor_agent"], 
                "session_id": session_id,
                "error": "No response from orchestrator"
            }

    except Exception as e:
        return {"status": "error", "error_message": str(e)}