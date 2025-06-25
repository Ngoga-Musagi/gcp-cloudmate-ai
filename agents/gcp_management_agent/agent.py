# # """
# # MIT License

# # Copyright (c) 2024 Ngoga Alexis

# # GCP Resource Management Agent using Google ADK.
# # This agent handles provisioning and deprovisioning of GCP resources.
# # Part of a multi-agent system for GCP management.
# # """

# # import os
# # from google.adk.agents import Agent
# # from google.cloud import storage
# # from dotenv import load_dotenv

# # # Load environment variables
# # load_dotenv()

# # """
# # MIT License

# # Copyright (c) 2024 Ngoga Alexis

# # GCP Resource Management Agent using Google ADK.
# # This agent handles provisioning and deprovisioning of GCP resources.
# # Part of a multi-agent system for GCP management.
# # """

# # import os
# # from google.adk.agents import Agent
# # from google.cloud import storage
# # from google.auth import default
# # from dotenv import load_dotenv

# # # Load environment variables
# # load_dotenv()

# # def create_storage_bucket(bucket_name: str, location: str = "US", storage_class: str = "STANDARD", 
# #                          versioning_enabled: bool = False):
# #     """
# #     Creates a Google Cloud Storage bucket with specified configuration.
    
# #     Args:
# #         bucket_name: Name of the bucket to create
# #         location: Location for the bucket (default: US)
# #         storage_class: Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
# #         versioning_enabled: Enable object versioning
        
# #     Returns:
# #         Dictionary containing operation status and details
# #     """
# #     try:
# #         # Get project ID
# #         project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
# #         if not project_id:
# #             return {
# #                 "status": "error",
# #                 "message": "GOOGLE_CLOUD_PROJECT environment variable not set. Please check your .env file.",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Check for credentials file
# #         creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# #         if not creds_path:
# #             return {
# #                 "status": "error",
# #                 "message": "GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Please check your .env file.",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         if not os.path.exists(creds_path):
# #             return {
# #                 "status": "error", 
# #                 "message": f"Credentials file not found at: {creds_path}. Please check the file path.",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Explicitly set the credentials
# #         os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
# #         # Get default credentials to verify they work
# #         try:
# #             credentials, auth_project = default()
# #             if auth_project:
# #                 project_id = auth_project
# #         except Exception as e:
# #             return {
# #                 "status": "error",
# #                 "message": f"Failed to authenticate with GCP: {str(e)}. Please check your credentials file.",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Initialize client with explicit credentials
# #         try:
# #             client = storage.Client(project=project_id, credentials=credentials)
# #         except Exception as e:
# #             return {
# #                 "status": "error",
# #                 "message": f"Failed to initialize GCP client: {str(e)}",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Check if bucket already exists
# #         try:
# #             bucket = client.get_bucket(bucket_name)
# #             return {
# #                 "status": "error",
# #                 "message": f"Bucket '{bucket_name}' already exists",
# #                 "resource_type": "storage_bucket"
# #             }
# #         except:
# #             # Bucket doesn't exist, we can create it
# #             pass
        
# #         # Create the bucket
# #         bucket = client.create_bucket(bucket_name, location=location)
# #         bucket.storage_class = storage_class
        
# #         # Configure versioning if requested
# #         if versioning_enabled:
# #             bucket.versioning_enabled = True
            
# #         bucket.patch()
        
# #         return {
# #             "status": "success",
# #             "message": f"Storage bucket '{bucket_name}' created successfully",
# #             "resource_type": "storage_bucket",
# #             "details": {
# #                 "name": bucket.name,
# #                 "location": bucket.location,
# #                 "storage_class": bucket.storage_class,
# #                 "versioning_enabled": bucket.versioning_enabled,
# #                 "created": str(bucket.time_created) if bucket.time_created else None,
# #                 "self_link": bucket.self_link
# #             }
# #         }
# #     except Exception as e:
# #         return {
# #             "status": "error",
# #             "message": f"Failed to create bucket: {str(e)}. Check credentials and permissions.",
# #             "resource_type": "storage_bucket"
# #         }

# # def delete_storage_bucket(bucket_name: str, force_delete_objects: bool = False):
# #     """
# #     Deletes a Google Cloud Storage bucket.
    
# #     Args:
# #         bucket_name: Name of the bucket to delete
# #         force_delete_objects: If True, deletes all objects in the bucket first
        
# #     Returns:
# #         Dictionary containing operation status and details
# #     """
# #     try:
# #         # Get project ID
# #         project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
# #         if not project_id:
# #             return {
# #                 "status": "error",
# #                 "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Check for credentials
# #         creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# #         if not creds_path or not os.path.exists(creds_path):
# #             return {
# #                 "status": "error",
# #                 "message": "GCP credentials not found. Please check your .env file.",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Explicitly set the credentials
# #         os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
# #         # Get default credentials
# #         try:
# #             credentials, auth_project = default()
# #             if auth_project:
# #                 project_id = auth_project
# #         except Exception as e:
# #             return {
# #                 "status": "error",
# #                 "message": f"Failed to authenticate with GCP: {str(e)}",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Initialize client with explicit credentials
# #         client = storage.Client(project=project_id, credentials=credentials)
# #         bucket = client.bucket(bucket_name)
        
# #         if not bucket.exists():
# #             return {
# #                 "status": "error",
# #                 "message": f"Bucket '{bucket_name}' does not exist",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Check if bucket has objects
# #         blobs = list(bucket.list_blobs(max_results=1))
# #         if blobs and not force_delete_objects:
# #             return {
# #                 "status": "error",
# #                 "message": f"Bucket '{bucket_name}' contains objects. Use force_delete_objects=True to delete them first",
# #                 "resource_type": "storage_bucket"
# #             }
        
# #         # Delete all objects if force is True
# #         if force_delete_objects:
# #             blobs = bucket.list_blobs()
# #             for blob in blobs:
# #                 blob.delete()
        
# #         bucket.delete()
        
# #         return {
# #             "status": "success",
# #             "message": f"Storage bucket '{bucket_name}' deleted successfully",
# #             "resource_type": "storage_bucket"
# #         }
        
# #     except Exception as e:
# #         return {
# #             "status": "error",
# #             "message": f"Failed to delete bucket: {str(e)}",
# #             "resource_type": "storage_bucket"
# #         }

# # def list_storage_buckets():
# #     """
# #     Lists all storage buckets in the project.
    
# #     Returns:
# #         Dictionary containing list of buckets and their details
# #     """
# #     try:
# #         # Get project ID
# #         project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
# #         if not project_id:
# #             return {
# #                 "status": "error",
# #                 "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
# #             }
        
# #         # Check for credentials
# #         creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
# #         if not creds_path or not os.path.exists(creds_path):
# #             return {
# #                 "status": "error",
# #                 "message": "GCP credentials not found. Please check your .env file."
# #             }
        
# #         # Explicitly set the credentials
# #         os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
# #         # Get default credentials
# #         try:
# #             credentials, auth_project = default()
# #             if auth_project:
# #                 project_id = auth_project
# #         except Exception as e:
# #             return {
# #                 "status": "error",
# #                 "message": f"Failed to authenticate with GCP: {str(e)}"
# #             }
        
# #         # Initialize client with explicit credentials
# #         client = storage.Client(project=project_id, credentials=credentials)
        
# #         # List all buckets
# #         buckets = list(client.list_buckets())
        
# #         bucket_list = []
# #         for bucket in buckets:
# #             bucket_info = {
# #                 "name": bucket.name,
# #                 "location": bucket.location,
# #                 "storage_class": bucket.storage_class,
# #                 "versioning_enabled": bucket.versioning_enabled,
# #                 "created": str(bucket.time_created) if bucket.time_created else None,
# #                 "updated": str(bucket.updated) if bucket.updated else None
# #             }
# #             bucket_list.append(bucket_info)
        
# #         return {
# #             "status": "success",
# #             "project_id": project_id,
# #             "bucket_count": len(bucket_list),
# #             "buckets": bucket_list
# #         }
        
# #     except Exception as e:
# #         return {
# #             "status": "error",
# #             "message": f"Failed to list buckets: {str(e)}"
# #         }

# # # Initialize the GCP Storage Management Agent
# # root_agent = Agent(
# #     name="gcp_storage_agent",
# #     model="gemini-1.5-flash",
# #     description="Specialized agent for managing Google Cloud Storage buckets. Can create, delete, and list storage buckets with various configurations.",
# #     instruction=(
# #         "You are a GCP Storage management agent that helps users create, delete, and list Google Cloud Storage buckets. "
# #         "You have access to three main functions: create_storage_bucket, delete_storage_bucket, and list_storage_buckets. "
# #         "\n\nYour capabilities:"
# #         "\n- Create storage buckets with custom configurations (location, storage class, versioning)"
# #         "\n- Delete storage buckets (with option to force delete objects)"
# #         "\n- List all existing storage buckets in the project"
# #         "\n- Provide clear status updates and error messages"
# #         "\n- Handle bucket naming requirements and conflicts"
# #         "\n\nWhen users request bucket operations:"
# #         "\n1. For listing: Use list_storage_buckets() to show all existing buckets"
# #         "\n2. For creation: Ask for required parameters (bucket name is mandatory)"
# #         "\n3. For deletion: Always warn about data loss and ask for confirmation"
# #         "\n4. Execute the requested operation using the appropriate tool"
# #         "\n5. Provide clear feedback on success or failure"
# #         "\n6. Include relevant details like bucket URL, location, and settings"
# #         "\n\nBucket naming rules to remember:"
# #         "\n- Must be globally unique across all of Google Cloud"
# #         "\n- Only lowercase letters, numbers, hyphens, and underscores"
# #         "\n- Must be 3-63 characters long"
# #         "\n- Cannot start or end with a hyphen"
# #     ),
# #     tools=[
# #         create_storage_bucket,
# #         delete_storage_bucket,
# #         list_storage_buckets
# #     ],
# # )


# # """
# # MIT License

# # Copyright (c) 2024 Ngoga Alexis

# # GCP Storage Management Agent using Google ADK.
# # This agent handles provisioning and deprovisioning of GCP Storage buckets only.
# # Part of a multi-agent system for GCP management.
# # """

# # import os
# # from typing import Dict
# # from google.adk.agents import Agent
# # from google.cloud import storage
# # from google.auth import default
# # from dotenv import load_dotenv

# # # Try to import Firestore - handle gracefully if not available
# # try:
# #     from google.cloud import firestore
# #     from google.cloud import exceptions
# #     from google.cloud import firestore_admin_v1
# #     from google.api_core import exceptions as api_exceptions
# #     from google.api_core.exceptions import AlreadyExists, NotFound, GoogleAPICallError
# #     from google.cloud.firestore_admin_v1.types import Database
# #     import time
# #     FIRESTORE_AVAILABLE = True
# # except ImportError:
# #     FIRESTORE_AVAILABLE = False
    
# # from .tools import create_storage_bucket,create_firestore_database, delete_firestore_database,delete_storage_bucket, list_storage_buckets,list_firestore_databases,list_all_firestore_databases


# # # Initialize the GCP Storage and Firestore Management Agent
# # root_agent = Agent(
# #     name="gcp_storage_firestore_agent",
# #     model="gemini-1.5-flash",
# #     description="Specialized agent for managing Google Cloud Storage buckets and Firestore databases. Can create, delete, and list storage buckets and manage Firestore databases, collections, and documents.",
# #     instruction=(
# #         "You are a GCP resource management agent that helps users manage Google Cloud Storage buckets and Firestore databases. "
# #         "You have access to seven main functions for storage and Firestore database operations. "
# #         "\n\nYour capabilities:"
# #         "\n\nStorage Buckets:"
# #         "\n- Create storage buckets with custom configurations (location, storage class, versioning)"
# #         "\n- Delete storage buckets (with option to force delete objects)"
# #         "\n- List all existing storage buckets in the project"
# #         "\n\nFirestore Database:"
# #         "\n- Create/initialize Firestore databases (default or named databases)"
# #         "\n- Delete named databases completely, or clear data from default database"
# #         "\n- List specific database information and collections"
# #         "\n- List ALL Firestore databases in the project (including named databases)"
# #         "\n\nWhen users request operations:"
# #         "\n1. For listing: Use appropriate list functions to show existing resources"
# #         "\n2. For creation: Ask for required parameters and suggest appropriate defaults"
# #         "\n3. For deletions: Always warn about data loss and ask for confirmation"
# #         "\n4. Execute the requested operation using the appropriate tool"
# #         "\n5. Provide clear feedback on success or failure with relevant details"
# #         "\n\nBucket naming rules:"
# #         "\n- Must be globally unique across all of Google Cloud"
# #         "\n- Only lowercase letters, numbers, hyphens, and underscores"
# #         "\n- Must be 3-63 characters long"
# #         "\n- Cannot start or end with a hyphen"
# #         "\n\nFirestore rules:"
# #         "\n- Collection names must be valid UTF-8 characters"
# #         "\n- Document IDs can be auto-generated or specified"
# #         "\n- Documents can contain nested objects, arrays, and various data types"
# #         "\n- Use subcollections for hierarchical data organization"
# #         "\n\nStorage classes available:"
# #         "\n- STANDARD: For frequently accessed data"
# #         "\n- NEARLINE: For data accessed less than once per month"
# #         "\n- COLDLINE: For data accessed less than once per quarter"
# #         "\n- ARCHIVE: For long-term archival and backup"
# #         "\n\nCommon locations:"
# #         "\n- US: Multi-region in United States"
# #         "\n- EU: Multi-region in European Union"
# #         "\n- ASIA: Multi-region in Asia"
# #         "\n- us-central1, us-east1, europe-west1, asia-southeast1: Single regions"
# #         "\n\nFirestore best practices:"
# #         "\n- Use meaningful collection and document names"
# #         "\n- Consider data structure and query patterns when designing collections"
# #         "\n- Remember that Firestore charges per read/write operation"
# #         "\n- Use batch operations for multiple document updates when possible"
# #     ),
# #     tools=[
# #         # Storage bucket tools
# #         create_storage_bucket,
# #         delete_storage_bucket,
# #         list_storage_buckets,
# #         # Firestore database tools
# #         create_firestore_database,
# #         delete_firestore_database,
# #         list_firestore_databases,
# #         list_all_firestore_databases
# #     ],
# # )
# """
# MIT License

# Copyright (c) 2024 Ngoga Alexis

# GCP Management Agent using Google ADK.
# This agent handles provisioning and management of GCP Storage buckets and Firestore databases.
# """

# import os
# import uuid
# import json
# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# from .tools import (
#     create_storage_bucket,
#     delete_storage_bucket,
#     list_storage_buckets,
#     create_firestore_database,
#     delete_firestore_database,
#     list_firestore_databases,
#     list_all_firestore_databases
# )

# # Define the agent
# root_agent = Agent(
#     name="gcp_management",
#     model="gemini-1.5-flash",
#     description="Agent that manages GCP Storage buckets and Firestore databases — create, delete, list resources with custom configs.",
#     instruction=(
#         "You are a GCP resource management agent that helps users manage Google Cloud Storage buckets and Firestore databases. "
#         "You have access to seven main functions for storage and Firestore database operations. "
#         "\n\nYour capabilities:"
#         "\n\nStorage Buckets:"
#         "\n- Create storage buckets with custom configurations (location, storage class, versioning)"
#         "\n- Delete storage buckets (with option to force delete objects)"
#         "\n- List all existing storage buckets in the project"
#         "\n\nFirestore Database:"
#         "\n- Create/initialize Firestore databases (default or named databases)"
#         "\n- Delete named databases completely, or clear data from default database"
#         "\n- List specific database information and collections"
#         "\n- List ALL Firestore databases in the project (including named databases)"
#         "\n\nWhen users request operations:"
#         "\n1. For listing: Use appropriate list functions to show existing resources"
#         "\n2. For creation: Ask for required parameters and suggest appropriate defaults"
#         "\n3. For deletions: Always warn about data loss and ask for confirmation"
#         "\n4. Execute the requested operation using the appropriate tool"
#         "\n5. Provide clear feedback on success or failure with relevant details"
#         "\n\nBucket naming rules:"
#         "\n- Must be globally unique across all of Google Cloud"
#         "\n- Only lowercase letters, numbers, hyphens, and underscores"
#         "\n- Must be 3-63 characters long"
#         "\n- Cannot start or end with a hyphen"
#         "\n\nFirestore rules:"
#         "\n- Collection names must be valid UTF-8 characters"
#         "\n- Document IDs can be auto-generated or specified"
#         "\n- Documents can contain nested objects, arrays, and various data types"
#         "\n- Use subcollections for hierarchical data organization"
#         "\n\nStorage classes available:"
#         "\n- STANDARD: For frequently accessed data"
#         "\n- NEARLINE: For data accessed less than once per month"
#         "\n- COLDLINE: For data accessed less than once per quarter"
#         "\n- ARCHIVE: For long-term archival and backup"
#         "\n\nCommon locations:"
#         "\n- US: Multi-region in United States"
#         "\n- EU: Multi-region in European Union"
#         "\n- ASIA: Multi-region in Asia"
#         "\n- us-central1, us-east1, europe-west1, asia-southeast1: Single regions"
#         "\n\nFirestore best practices:"
#         "\n- Use meaningful collection and document names"
#         "\n- Consider data structure and query patterns when designing collections"
#         "\n- Remember that Firestore charges per read/write operation"
#         "\n- Use batch operations for multiple document updates when possible"
#     ),
#     tools=[
#         create_storage_bucket,
#         delete_storage_bucket,
#         list_storage_buckets,
#         create_firestore_database,
#         delete_firestore_database,
#         list_firestore_databases,
#         list_all_firestore_databases
#     ]
# )

# # Session + runner setup
# session_service = InMemorySessionService()
# runner = Runner(
#     agent=root_agent,
#     app_name="gcp_management_app",
#     session_service=session_service
# )

# USER_ID = "user_gcp_management"

# # Async entrypoint
# async def execute(request):
#     try:
#         if "prompt" not in request:
#             return {"status": "error", "error_message": "Missing 'prompt' in request."}

#         session_id = f"session_{uuid.uuid4().hex[:8]}"
#         await session_service.create_session("gcp_management_app", USER_ID, session_id)

#         user_message = types.Content(role="user", parts=[types.Part(text=request["prompt"])])
#         final_response = None

#         async for event in runner.run_async(USER_ID, session_id, new_message=user_message):
#             if event.is_final_response():
#                 final_response = event.content.parts[0].text
#                 break

#         await session_service.delete_session("gcp_management_app", USER_ID, session_id)

#         if final_response:
#             try:
#                 parsed = json.loads(final_response)
#                 return parsed if isinstance(parsed, dict) else {"response": final_response}
#             except json.JSONDecodeError:
#                 return {"response": final_response}
#         else:
#             return {"status": "error", "error_message": "No final response received."}
#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}


# """
# MIT License

# Copyright (c) 2024 Ngoga Alexis

# GCP Management Agent using Google ADK.
# This agent handles provisioning and management of GCP Storage buckets and Firestore databases.
# """

# import os
# import uuid
# import json
# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types

# from .tools import (
#     create_storage_bucket,
#     delete_storage_bucket,
#     list_storage_buckets,
#     create_firestore_database,
#     delete_firestore_database,
#     list_firestore_databases,
#     list_all_firestore_databases
# )

# # Define the agent
# root_agent = Agent(
#     name="gcp_management",
#     model="gemini-1.5-flash",
#     description="Agent that manages GCP Storage buckets and Firestore databases — create, delete, list resources with custom configs.",
#     instruction=(
#         "You are a GCP resource management agent that helps users manage Google Cloud Storage buckets and Firestore databases. "
#         "You have access to seven main functions for storage and Firestore database operations. "
#         "\n\nYour capabilities:"
#         "\n\nStorage Buckets:"
#         "\n- Create storage buckets with custom configurations (location, storage class, versioning)"
#         "\n- Delete storage buckets (with option to force delete objects)"
#         "\n- List all existing storage buckets in the project"
#         "\n\nFirestore Database:"
#         "\n- Create/initialize Firestore databases (default or named databases)"
#         "\n- Delete named databases completely, or clear data from default database"
#         "\n- List specific database information and collections"
#         "\n- List ALL Firestore databases in the project (including named databases)"
#         "\n\nWhen users request operations:"
#         "\n1. For listing: Use appropriate list functions to show existing resources"
#         "\n2. For creation: Ask for required parameters and suggest appropriate defaults"
#         "\n3. For deletions: Always warn about data loss and ask for confirmation"
#         "\n4. Execute the requested operation using the appropriate tool"
#         "\n5. Provide clear feedback on success or failure with relevant details"
#         "\n\nBucket naming rules:"
#         "\n- Must be globally unique across all of Google Cloud"
#         "\n- Only lowercase letters, numbers, hyphens, and underscores"
#         "\n- Must be 3-63 characters long"
#         "\n- Cannot start or end with a hyphen"
#         "\n\nFirestore rules:"
#         "\n- Collection names must be valid UTF-8 characters"
#         "\n- Document IDs can be auto-generated or specified"
#         "\n- Documents can contain nested objects, arrays, and various data types"
#         "\n- Use subcollections for hierarchical data organization"
#         "\n\nStorage classes available:"
#         "\n- STANDARD: For frequently accessed data"
#         "\n- NEARLINE: For data accessed less than once per month"
#         "\n- COLDLINE: For data accessed less than once per quarter"
#         "\n- ARCHIVE: For long-term archival and backup"
#         "\n\nCommon locations:"
#         "\n- US: Multi-region in United States"
#         "\n- EU: Multi-region in European Union"
#         "\n- ASIA: Multi-region in Asia"
#         "\n- us-central1, us-east1, europe-west1, asia-southeast1: Single regions"
#         "\n\nFirestore best practices:"
#         "\n- Use meaningful collection and document names"
#         "\n- Consider data structure and query patterns when designing collections"
#         "\n- Remember that Firestore charges per read/write operation"
#         "\n- Use batch operations for multiple document updates when possible"
#     ),
#     tools=[
#         create_storage_bucket,
#         delete_storage_bucket,
#         list_storage_buckets,
#         create_firestore_database,
#         delete_firestore_database,
#         list_firestore_databases,
#         list_all_firestore_databases
#     ]
# )

# # Session + runner setup
# session_service = InMemorySessionService()
# runner = Runner(
#     agent=root_agent,
#     app_name="gcp_management_app",
#     session_service=session_service
# )

# USER_ID = "user_gcp_management"

# # Async entrypoint
# async def execute(request):
#     try:
#         if "prompt" not in request:
#             return {"status": "error", "error_message": "Missing 'prompt' in request."}

#         session_id = f"session_{uuid.uuid4().hex[:8]}"
        
#         # FIX: Use keyword arguments for create_session (same pattern as gcp_advisor_agent)
#         await session_service.create_session(
#             app_name="gcp_management_app",
#             user_id=USER_ID,
#             session_id=session_id
#         )

#         user_message = types.Content(role="user", parts=[types.Part(text=request["prompt"])])
#         final_response = None

#         async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=user_message):
#             if event.is_final_response():
#                 final_response = event.content.parts[0].text
#                 break

#         # FIX: Use keyword arguments for delete_session too
#         try:
#             await session_service.delete_session(
#                 app_name="gcp_management_app",
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
#             return {"status": "error", "error_message": "No final response received."}
#     except Exception as e:
#         return {"status": "error", "error_message": str(e)}


"""
MIT License

Copyright (c) 2024 Ngoga Alexis

GCP Management Agent using Google ADK.
This agent handles provisioning and management of GCP Storage buckets and Firestore databases.
"""

import os
import uuid
import json
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .tools import (
    create_storage_bucket,
    delete_storage_bucket,
    list_storage_buckets,
    create_firestore_database,
    delete_firestore_database,
    list_firestore_databases,
    list_all_firestore_databases
)

# Define the agent
root_agent = Agent(
    name="gcp_management",
    model="gemini-1.5-flash",
    description="Agent that manages GCP Storage buckets and Firestore databases — create, delete, list resources with custom configs.",
    instruction=(
        "You are a GCP resource management agent that helps users manage Google Cloud Storage buckets and Firestore databases. "
        "You have access to seven main functions for storage and Firestore database operations. "
        "\n\nYour capabilities:"
        "\n\nStorage Buckets:"
        "\n- Create storage buckets with custom configurations (location, storage class, versioning)"
        "\n- Delete storage buckets (with option to force delete objects)"
        "\n- List all existing storage buckets in the project"
        "\n\nFirestore Database:"
        "\n- Create/initialize Firestore databases (default or named databases)"
        "\n- Delete named databases completely, or clear data from default database"
        "\n- List specific database information and collections"
        "\n- List ALL Firestore databases in the project (including named databases)"
        "\n\nWhen users request operations:"
        "\n1. For listing: Use appropriate list functions to show existing resources"
        "\n2. For creation: Ask for required parameters and suggest appropriate defaults"
        "\n3. For deletions: Always warn about data loss and ask for confirmation"
        "\n4. Execute the requested operation using the appropriate tool"
        "\n5. Provide clear feedback on success or failure with relevant details"
        "\n\nBucket naming rules:"
        "\n- Must be globally unique across all of Google Cloud"
        "\n- Only lowercase letters, numbers, hyphens, and underscores"
        "\n- Must be 3-63 characters long"
        "\n- Cannot start or end with a hyphen"
        "\n\nFirestore rules:"
        "\n- Collection names must be valid UTF-8 characters"
        "\n- Document IDs can be auto-generated or specified"
        "\n- Documents can contain nested objects, arrays, and various data types"
        "\n- Use subcollections for hierarchical data organization"
        "\n\nStorage classes available:"
        "\n- STANDARD: For frequently accessed data"
        "\n- NEARLINE: For data accessed less than once per month"
        "\n- COLDLINE: For data accessed less than once per quarter"
        "\n- ARCHIVE: For long-term archival and backup"
        "\n\nCommon locations:"
        "\n- US: Multi-region in United States"
        "\n- EU: Multi-region in European Union"
        "\n- ASIA: Multi-region in Asia"
        "\n- us-central1, us-east1, europe-west1, asia-southeast1: Single regions"
        "\n\nFirestore best practices:"
        "\n- Use meaningful collection and document names"
        "\n- Consider data structure and query patterns when designing collections"
        "\n- Remember that Firestore charges per read/write operation"
        "\n- Use batch operations for multiple document updates when possible"
    ),
    tools=[
        create_storage_bucket,
        delete_storage_bucket,
        list_storage_buckets,
        create_firestore_database,
        delete_firestore_database,
        list_firestore_databases,
        list_all_firestore_databases
    ]
)

# Session + runner setup
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="gcp_management_app",
    session_service=session_service
)

USER_ID = "user_gcp_management"

# Async entrypoint
async def execute(request):
    try:
        if "prompt" not in request:
            return {"status": "error", "error_message": "Missing 'prompt' in request."}

        # CHANGED: Use provided session_id or create persistent one per user
        session_id = request.get("session_id", f"persistent_session_{USER_ID}")
        
        # CHANGED: Only create session if it doesn't already exist
        try:
            await session_service.create_session(
                app_name="gcp_management_app",
                user_id=USER_ID,
                session_id=session_id
            )
        except Exception:
            # Session likely already exists, which is fine
            pass

        user_message = types.Content(role="user", parts=[types.Part(text=request["prompt"])])
        final_response = None

        async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=user_message):
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break

        # CHANGED: Don't delete session - keep it alive for follow-up conversations
        if request.get("end_conversation", False):
            try:
                await session_service.delete_session(
                    app_name="gcp_management_app",
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
            return {"status": "error", "error_message": "No final response received.", "session_id": session_id}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
