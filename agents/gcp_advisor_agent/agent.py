# """
# MIT License

# Copyright (c) 2024 Ngoga Alexis

# This is an educational example demonstrating a GCP Advisor Agent using Google ADK.
# The agent helps users choose appropriate GCP services based on their requirements.
# """

# from typing import Dict, List, Optional
# import json
# import requests
# from google.adk.agents import Agent
# from os import getenv
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# def search_gcp_services(use_case: str, budget_range: Optional[str] = None, requirements: Optional[str] = None) -> Dict:
#     """
#     Searches and recommends GCP services based on use case, budget, and requirements.
    
#     Args:
#         use_case: The primary use case or problem to solve
#         budget_range: Optional budget constraints (e.g., "low", "medium", "high")
#         requirements: Additional technical or business requirements
        
#     Returns:
#         Dictionary containing recommendations and explanations
#     """
#     try:
#         # Format the search query to get relevant GCP information
#         search_query = f"Google Cloud Platform services for {use_case}"
#         if budget_range:
#             search_query += f" with {budget_range} budget"
#         if requirements:
#             search_query += f" with {requirements}"

#         # Perform web search to get real-time GCP information
#         search_results = requests.get(
#             "https://www.googleapis.com/customsearch/v1",
#             params={
#                 'key': getenv('GOOGLE_SEARCH_API_KEY'),
#                 'cx': getenv('GOOGLE_SEARCH_ENGINE_ID'),
#                 'q': search_query
#             }
#         ).json()

#         # Process and analyze search results
#         recommendations = {
#             "primary_services": [],
#             "alternative_services": [],
#             "estimated_costs": "",
#             "architecture_tips": [],
#             "best_practices": []
#         }

#         # Extract relevant information from search results
#         for item in search_results.get('items', []):
#             if 'cloud.google.com' in item.get('link', ''):
#                 # Parse official GCP documentation
#                 if 'solutions' in item['link']:
#                     recommendations['architecture_tips'].append({
#                         'title': item['title'],
#                         'link': item['link'],
#                         'description': item['snippet']
#                     })
#                 elif 'products' in item['link']:
#                     recommendations['primary_services'].append({
#                         'name': item['title'],
#                         'description': item['snippet'],
#                         'link': item['link']
#                     })

#         return {
#             "status": "success",
#             "recommendations": recommendations
#         }
#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}

# def estimate_costs(services: List[str]) -> Dict:
#     """
#     Provides rough cost estimates for recommended GCP services.
    
#     Args:
#         services: List of GCP services to estimate costs for
        
#     Returns:
#         Dictionary containing cost estimates and pricing details
#     """
#     try:
#         # Search for pricing information for each service
#         cost_estimates = {
#             "monthly_estimate": {},
#             "pricing_breakdown": {},
#             "cost_optimization_tips": []
#         }

#         for service in services:
#             # Get real-time pricing information from GCP
#             pricing_query = f"Google Cloud {service} pricing calculator"
#             search_results = requests.get(
#                 "https://www.googleapis.com/customsearch/v1",
#                 params={
#                     'key': getenv('GOOGLE_SEARCH_API_KEY'),
#                     'cx': getenv('GOOGLE_SEARCH_ENGINE_ID'),
#                     'q': pricing_query
#                 }
#             ).json()

#             # Extract pricing information
#             for item in search_results.get('items', []):
#                 if 'cloud.google.com/pricing' in item.get('link', ''):
#                     cost_estimates['pricing_breakdown'][service] = {
#                         'pricing_page': item['link'],
#                         'summary': item['snippet']
#                     }

#             # Add common cost optimization tips
#             cost_estimates['cost_optimization_tips'].extend([
#                 f"Consider using committed use discounts for {service} if you plan long-term usage",
#                 f"Monitor usage patterns and set up budget alerts for {service}",
#                 f"Use GCP's built-in cost optimization recommendations for {service}"
#             ])

#         return {
#             "status": "success",
#             "cost_estimates": cost_estimates
#         }
#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}

# def get_compliance_info(industry: str) -> Dict:
#     """
#     Retrieves compliance and security information for specific industries.
    
#     Args:
#         industry: The industry sector (e.g., "healthcare", "finance", "retail")
        
#     Returns:
#         Dictionary containing compliance requirements and recommendations
#     """
#     try:
#         search_query = f"Google Cloud Platform compliance {industry} industry requirements"
#         search_results = requests.get(
#             "https://www.googleapis.com/customsearch/v1",
#             params={
#                 'key': getenv('GOOGLE_SEARCH_API_KEY'),
#                 'cx': getenv('GOOGLE_SEARCH_ENGINE_ID'),
#                 'q': search_query
#             }
#         ).json()

#         compliance_info = {
#             "requirements": [],
#             "certifications": [],
#             "best_practices": []
#         }

#         for item in search_results.get('items', []):
#             if 'cloud.google.com/security' in item.get('link', '') or 'cloud.google.com/compliance' in item.get('link', ''):
#                 compliance_info['requirements'].append({
#                     'title': item['title'],
#                     'link': item['link'],
#                     'description': item['snippet']
#                 })

#         return {
#             "status": "success",
#             "compliance_info": compliance_info
#         }
#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}

# # Initialize the GCP Advisor Agent
# # gcp_advisor = Agent(
# root_agent = Agent(
#     name="gcp_advisor",
#     model="gemini-1.5-flash",  # or gemini-2.0-pro if available
#     description="An intelligent agent that provides personalized GCP service recommendations based on user requirements.",
#     instruction=(
#         "You are a knowledgeable Google Cloud Platform advisor. "
#         "Help users choose the most suitable GCP services based on their use cases, "
#         "budget constraints, and technical requirements. "
#         "\n\nWhen users describe their needs:"
#         "\n1. Ask clarifying questions about their use case if needed"
#         "\n2. Request budget range if not provided"
#         "\n3. Gather any specific technical requirements"
#         "\n4. Use the search_gcp_services tool to find relevant solutions"
#         "\n5. Provide cost estimates using the estimate_costs tool"
#         "\n6. Check compliance requirements if applicable"
#         "\n7. Explain your recommendations in a clear, structured way"
#         "\n\nAdditional guidelines:"
#         "\n- Always consider the user's budget constraints"
#         "\n- Suggest alternative services when appropriate"
#         "\n- Provide architecture best practices"
#         "\n- Include links to relevant documentation"
#         "\n- Offer cost optimization tips"
#         "\n- Consider industry-specific compliance needs"
#     ),
#     tools=[search_gcp_services, estimate_costs, get_compliance_info],
# ) 


# gcp_advisor_agent/agent.py

# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# from .tools import search_gcp_services, estimate_costs, get_compliance_info

# import uuid
# import json

# # Define the agent
# root_agent = Agent(
#     name="gcp_advisor",
#     # model=LiteLlm("gemini-1.5-flash"),
#     model="gemini-1.5-flash",
#     description="Provides personalized GCP service recommendations based on user requirements, budget, and industry.",
#     instruction=(
#         "You are a knowledgeable Google Cloud Platform advisor. "
#         "Help users choose the most suitable GCP services based on their use cases, "
#         "budget constraints, and technical requirements. "
#         "\n\nWhen users describe their needs:"
#         "\n1. Ask clarifying questions about their use case if needed"
#         "\n2. Request budget range if not provided"
#         "\n3. Gather any specific technical requirements"
#         "\n4. Use the search_gcp_services tool to find relevant solutions"
#         "\n5. Provide cost estimates using the estimate_costs tool"
#         "\n6. Check compliance requirements if applicable"
#         "\n7. Explain your recommendations in a clear, structured way"
#         "\n\nGuidelines:"
#         "\n- Consider the user's budget and scale needs"
#         "\n- Suggest alternatives when appropriate"
#         "\n- Include relevant links, cost tips, and compliance notes"
#     ),
#     tools=[search_gcp_services, estimate_costs, get_compliance_info]
# )

# # Setup session management and runner
# session_service = InMemorySessionService()
# runner = Runner(
#     agent=root_agent,
#     app_name="gcp_advisor_app",
#     session_service=session_service
# )

# USER_ID = "user_gcp_advisor"

# async def execute(request):
#     try:
#         if "prompt" not in request:
#             return {"status": "error", "error_message": "Missing 'prompt' in request."}

#         session_id = f"session_{uuid.uuid4().hex[:8]}"

#         await session_service.create_session(
#             app_name="gcp_advisor_app",
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
#                 app_name="gcp_advisor_app",
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


from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .tools import search_gcp_services, estimate_costs, get_compliance_info

import uuid
import json

# Define the agent
root_agent = Agent(
    name="gcp_advisor",
    # model=LiteLlm("gemini-1.5-flash"),
    model="gemini-1.5-flash",
    description="Provides personalized GCP service recommendations based on user requirements, budget, and industry.",
    instruction=(
        "You are a knowledgeable Google Cloud Platform advisor. "
        "Help users choose the most suitable GCP services based on their use cases, "
        "budget constraints, and technical requirements. "
        "\n\nWhen users describe their needs:"
        "\n1. Ask clarifying questions about their use case if needed"
        "\n2. Request budget range if not provided"
        "\n3. Gather any specific technical requirements"
        "\n4. Use the search_gcp_services tool to find relevant solutions"
        "\n5. Provide cost estimates using the estimate_costs tool"
        "\n6. Check compliance requirements if applicable"
        "\n7. Explain your recommendations in a clear, structured way"
        "\n\nGuidelines:"
        "\n- Consider the user's budget and scale needs"
        "\n- Suggest alternatives when appropriate"
        "\n- Include relevant links, cost tips, and compliance notes"
    ),
    tools=[search_gcp_services, estimate_costs, get_compliance_info]
)

# Setup session management and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="gcp_advisor_app",
    session_service=session_service
)

USER_ID = "user_gcp_advisor"

async def execute(request):
    try:
        if "prompt" not in request:
            return {"status": "error", "error_message": "Missing 'prompt' in request."}

        # CHANGED: Use provided session_id or create persistent one per user
        session_id = request.get("session_id", f"persistent_session_{USER_ID}")

        # CHANGED: Only create session if it doesn't already exist
        try:
            await session_service.create_session(
                app_name="gcp_advisor_app",
                user_id=USER_ID,
                session_id=session_id
            )
        except Exception:
            # Session likely already exists, which is fine
            pass

        # Wrap user prompt in a Content message
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
                    app_name="gcp_advisor_app",
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