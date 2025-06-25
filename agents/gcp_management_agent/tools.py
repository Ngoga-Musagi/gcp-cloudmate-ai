
"""
MIT License

Copyright (c) 2024 Ngoga Alexis

GCP Storage Management Agent using Google ADK.
This agent handles provisioning and deprovisioning of GCP Storage buckets only.
Part of a multi-agent system for GCP management.
"""

import os
from typing import Dict
from google.adk.agents import Agent
from google.cloud import storage
from google.auth import default
from dotenv import load_dotenv

# Try to import Firestore - handle gracefully if not available
try:
    from google.cloud import firestore
    from google.cloud import exceptions
    from google.cloud import firestore_admin_v1
    from google.api_core import exceptions as api_exceptions
    from google.api_core.exceptions import AlreadyExists, NotFound, GoogleAPICallError
    from google.cloud.firestore_admin_v1.types import Database
    import time
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    
    
# Load environment variables
load_dotenv()

def create_storage_bucket(bucket_name: str, location: str = "US", storage_class: str = "STANDARD", 
                         versioning_enabled: bool = False):
    """
    Creates a Google Cloud Storage bucket with specified configuration.
    
    Args:
        bucket_name: Name of the bucket to create
        location: Location for the bucket (default: US)
        storage_class: Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
        versioning_enabled: Enable object versioning
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        # Get project ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set. Please check your .env file.",
                "resource_type": "storage_bucket"
            }
        
        # Check for credentials file
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path:
            return {
                "status": "error",
                "message": "GOOGLE_APPLICATION_CREDENTIALS environment variable not set. Please check your .env file.",
                "resource_type": "storage_bucket"
            }
        
        if not os.path.exists(creds_path):
            return {
                "status": "error", 
                "message": f"Credentials file not found at: {creds_path}. Please check the file path.",
                "resource_type": "storage_bucket"
            }
        
        # Explicitly set the credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        # Get default credentials to verify they work
        try:
            credentials, auth_project = default()
            if auth_project:
                project_id = auth_project
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to authenticate with GCP: {str(e)}. Please check your credentials file.",
                "resource_type": "storage_bucket"
            }
        
        # Initialize client with explicit credentials
        try:
            client = storage.Client(project=project_id, credentials=credentials)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize GCP client: {str(e)}",
                "resource_type": "storage_bucket"
            }
        
        # Check if bucket already exists
        try:
            bucket = client.get_bucket(bucket_name)
            return {
                "status": "error",
                "message": f"Bucket '{bucket_name}' already exists",
                "resource_type": "storage_bucket"
            }
        except:
            # Bucket doesn't exist, we can create it
            pass
        
        # Create the bucket
        bucket = client.create_bucket(bucket_name, location=location)
        bucket.storage_class = storage_class
        
        # Configure versioning if requested
        if versioning_enabled:
            bucket.versioning_enabled = True
            
        bucket.patch()
        
        return {
            "status": "success",
            "message": f"Storage bucket '{bucket_name}' created successfully",
            "resource_type": "storage_bucket",
            "details": {
                "name": bucket.name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "versioning_enabled": bucket.versioning_enabled,
                "created": str(bucket.time_created) if bucket.time_created else None,
                "self_link": bucket.self_link
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create bucket: {str(e)}. Check credentials and permissions.",
            "resource_type": "storage_bucket"
        }

def delete_storage_bucket(bucket_name: str, force_delete_objects: bool = False):
    """
    Deletes a Google Cloud Storage bucket.
    
    Args:
        bucket_name: Name of the bucket to delete
        force_delete_objects: If True, deletes all objects in the bucket first
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        # Get project ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "storage_bucket"
            }
        
        # Check for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            return {
                "status": "error",
                "message": "GCP credentials not found. Please check your .env file.",
                "resource_type": "storage_bucket"
            }
        
        # Explicitly set the credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        # Get default credentials
        try:
            credentials, auth_project = default()
            if auth_project:
                project_id = auth_project
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to authenticate with GCP: {str(e)}",
                "resource_type": "storage_bucket"
            }
        
        # Initialize client with explicit credentials
        client = storage.Client(project=project_id, credentials=credentials)
        bucket = client.bucket(bucket_name)
        
        if not bucket.exists():
            return {
                "status": "error",
                "message": f"Bucket '{bucket_name}' does not exist",
                "resource_type": "storage_bucket"
            }
        
        # Check if bucket has objects
        blobs = list(bucket.list_blobs(max_results=1))
        if blobs and not force_delete_objects:
            return {
                "status": "error",
                "message": f"Bucket '{bucket_name}' contains objects. Use force_delete_objects=True to delete them first",
                "resource_type": "storage_bucket"
            }
        
        # Delete all objects if force is True
        if force_delete_objects:
            blobs = bucket.list_blobs()
            for blob in blobs:
                blob.delete()
        
        bucket.delete()
        
        return {
            "status": "success",
            "message": f"Storage bucket '{bucket_name}' deleted successfully",
            "resource_type": "storage_bucket"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete bucket: {str(e)}",
            "resource_type": "storage_bucket"
        }

def list_storage_buckets():
    """
    Lists all storage buckets in the project.
    
    Returns:
        Dictionary containing list of buckets and their details
    """
    try:
        # Get project ID
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
            }
        
        # Check for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            return {
                "status": "error",
                "message": "GCP credentials not found. Please check your .env file."
            }
        
        # Explicitly set the credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        # Get default credentials
        try:
            credentials, auth_project = default()
            if auth_project:
                project_id = auth_project
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to authenticate with GCP: {str(e)}"
            }
        
        # Initialize client with explicit credentials
        client = storage.Client(project=project_id, credentials=credentials)
        
        # List all buckets
        buckets = list(client.list_buckets())
        
        bucket_list = []
        for bucket in buckets:
            bucket_info = {
                "name": bucket.name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "versioning_enabled": bucket.versioning_enabled,
                "created": str(bucket.time_created) if bucket.time_created else None,
                "updated": str(bucket.updated) if bucket.updated else None
            }
            bucket_list.append(bucket_info)
        
        return {
            "status": "success",
            "project_id": project_id,
            "bucket_count": len(bucket_list),
            "buckets": bucket_list
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list buckets: {str(e)}"
        }



def create_firestore_database(database_id: str = "(default)", location_id: str = "nam5", 
                             database_type: str = "FIRESTORE_NATIVE") -> Dict:
    """
    Creates a Firestore database (default or named database).
    
    Args:
        database_id: ID for the database (default: "(default)" for default database)
        location_id: Location for the database (default: "nam5" - North America)
        database_type: Type of database (FIRESTORE_NATIVE or DATASTORE_MODE)
        
    Returns:
        Dictionary containing operation status and details
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Install: pip install google-cloud-firestore",
            "resource_type": "firestore_database"
        }
    
    try:
        # Check for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        credentials, project_id = default()
        
        if database_id == "(default)":
            # Handle default database creation/initialization
            db = firestore.Client(project=project_id, credentials=credentials)
            db.collection("init_check").document("ping").set({"status": "initialized"})
            
            return {
                "status": "success",
                "message": f"Default Firestore initialized in project {project_id}",
                "resource_type": "firestore_database",
                "details": {
                    "project_id": project_id,
                    "database_id": database_id,
                    "status": "active"
                }
            }
        
        # Named database creation
        admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)
        parent = f"projects/{project_id}"
        db_path = f"{parent}/databases/{database_id}"
        
        try:
            admin_client.get_database(name=db_path)
            return {
                "status": "error",
                "message": f"Named database '{database_id}' already exists",
                "resource_type": "firestore_database"
            }
        except NotFound:
            pass  # Safe to create
        
        # Use the correct enum for database type
        db_type = Database.DatabaseType.FIRESTORE_NATIVE if database_type == "FIRESTORE_NATIVE" \
            else Database.DatabaseType.DATASTORE_MODE
        
        request = firestore_admin_v1.types.CreateDatabaseRequest(
            parent=parent,
            database_id=database_id,
            database=Database(
                location_id=location_id,
                type_=db_type
            )
        )
        
        op = admin_client.create_database(request=request)
        result = op.result(timeout=300)
        
        return {
            "status": "success",
            "message": f"Named database '{database_id}' created successfully",
            "resource_type": "firestore_database",
            "details": {
                "project_id": project_id,
                "database_id": database_id,
                "name": result.name,
                "location_id": result.location_id,
                "type": result.type_.name,
                "create_time": str(result.create_time) if result.create_time else None
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create Firestore database: {str(e)}",
            "resource_type": "firestore_database",
            "error_type": str(type(e).__name__)
        }

def delete_firestore_database(database_id: str = "(default)") -> Dict:
    """
    Deletes a Firestore database completely or clears all data from default database.
    
    Args:
        database_id: ID of the database (default: "(default)")
        
    Returns:
        Dictionary containing operation status and details
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Install: pip install google-cloud-firestore",
            "resource_type": "firestore_database"
        }
    
    try:
        # Check for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        credentials, project_id = default()
        
        if database_id == "(default)":
            # For default database, clear all data (cannot delete the default database)
            db = firestore.Client(project=project_id, credentials=credentials)
            cleared = 0
            deleted_collections = []
            
            for col in db.collections():
                collection_name = col.id
                docs_deleted = 0
                for doc in col.stream():
                    doc.reference.delete()
                    docs_deleted += 1
                    cleared += 1
                
                deleted_collections.append({
                    "collection": collection_name,
                    "documents_deleted": docs_deleted
                })
            
            return {
                "status": "success",
                "message": f"Cleared {cleared} documents from default Firestore database",
                "resource_type": "firestore_database",
                "details": {
                    "project_id": project_id,
                    "database_id": database_id,
                    "total_documents_cleared": cleared,
                    "collections_cleared": len(deleted_collections),
                    "deleted_collections": deleted_collections,
                    "note": "Default database structure remains, only data was deleted"
                }
            }
        else:
            # For named databases, delete the entire database
            admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)
            db_path = f"projects/{project_id}/databases/{database_id}"
            
            try:
                admin_client.get_database(name=db_path)
                op = admin_client.delete_database(name=db_path)
                
                # Manual polling with extended timeout
                timeout = 600  # 10 minutes
                start_time = time.time()
                
                print(f"⏳ Waiting for deletion of database '{database_id}'...")
                
                while not op.done():
                    if time.time() - start_time > timeout:
                        return {
                            "status": "timeout",
                            "message": f"Timed out waiting for database '{database_id}' to be deleted",
                            "resource_type": "firestore_database"
                        }
                    time.sleep(10)
                
                op.result()  # ensure it's successful
                
                return {
                    "status": "success",
                    "message": f"Firestore database '{database_id}' deleted successfully",
                    "resource_type": "firestore_database",
                    "details": {
                        "project_id": project_id,
                        "database_id": database_id,
                        "note": "Database and all its data have been permanently deleted"
                    }
                }
                
            except NotFound:
                return {
                    "status": "error",
                    "message": f"Named database '{database_id}' does not exist",
                    "resource_type": "firestore_database"
                }
            except GoogleAPICallError as e:
                return {
                    "status": "error",
                    "message": f"Database deletion failed: {str(e)}",
                    "resource_type": "firestore_database"
                }
            except TimeoutError as e:
                return {
                    "status": "timeout",
                    "message": str(e),
                    "resource_type": "firestore_database"
                }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete Firestore database: {str(e)}",
            "resource_type": "firestore_database",
            "error_type": str(type(e).__name__)
        }

def list_firestore_databases(database_id: str = "(default)") -> Dict:
    """
    Shows specific Firestore database information and collections.
    
    Args:
        database_id: ID of the database to show (default: "(default)")
        
    Returns:
        Dictionary containing database information and collections
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Install: pip install google-cloud-firestore"
        }
    
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
            }
        
        # Check for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        # Get default credentials
        try:
            credentials, auth_project = default()
            if auth_project:
                project_id = auth_project
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to authenticate with GCP: {str(e)}"
            }
        
        # Initialize Firestore client for specific database
        if database_id == "(default)":
            db = firestore.Client(project=project_id, credentials=credentials)
        else:
            db = firestore.Client(project=project_id, database=database_id, credentials=credentials)
        
        # Get all collections in the database
        collections = list(db.collections())
        collection_info = []
        
        for collection in collections:
            # Count documents in each collection (limit for performance)
            docs = list(collection.limit(100).stream())
            
            collection_info.append({
                "collection_id": collection.id,
                "document_count": len(docs),
                "document_count_note": "Limited to first 100 documents for performance",
                "path": collection.path
            })
        
        # Get database metadata if it's a named database
        database_metadata = {}
        if database_id != "(default)":
            try:
                admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)
                database_path = f"projects/{project_id}/databases/{database_id}"
                db_info = admin_client.get_database(name=database_path)
                
                database_metadata = {
                    "location_id": db_info.location_id,
                    "type": db_info.type_.name if db_info.type_ else "UNKNOWN",
                    "create_time": str(db_info.create_time) if db_info.create_time else None,
                    "update_time": str(db_info.update_time) if db_info.update_time else None,
                    "state": db_info.state.name if db_info.state else "UNKNOWN"
                }
            except Exception as e:
                database_metadata = {"metadata_error": f"Could not retrieve metadata: {str(e)}"}
        
        return {
            "status": "success",
            "project_id": project_id,
            "database_info": {
                "database_id": database_id,
                "type": database_metadata.get("type", "FIRESTORE_NATIVE"),
                "status": "active" if collections or True else "empty",
                "collections_count": len(collection_info),
                **database_metadata
            },
            "collections": collection_info
        }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and Firestore permissions"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get Firestore database information: {str(e)}"
        }

def list_all_firestore_databases() -> Dict:
    """
    Lists all Firestore databases in the project, including named databases.
    
    Returns:
        Dictionary containing all databases in the project
    """
    if not FIRESTORE_AVAILABLE:
        return {
            "status": "error",
            "message": "Firestore not available. Install: pip install google-cloud-firestore",
            "resource_type": "firestore_databases"
        }
    
    try:
        # Check for credentials
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if creds_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        credentials, project_id = default()
        admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)
        
        response = admin_client.list_databases(parent=f"projects/{project_id}")
        db_list = []
        
        for db in response.databases:
            # Extract database info
            database_info = {
                "name": db.name,
                "database_id": db.name.split("/")[-1],
                "type": getattr(db.type_, "name", "UNKNOWN"),
                "state": getattr(db.state, "name", "UNKNOWN") if hasattr(db, "state") else "UNKNOWN",
                "location_id": db.location_id,
                "create_time": str(db.create_time) if db.create_time else None,
                "update_time": str(db.update_time) if db.update_time else None,
                "etag": db.etag if hasattr(db, "etag") else None
            }
            
            # Try to get collection count for each database (if accessible)
            try:
                if database_info["database_id"] == "(default)":
                    # Use regular client for default database
                    db_client = firestore.Client(project=project_id, credentials=credentials)
                else:
                    # Use named database client
                    db_client = firestore.Client(
                        project=project_id, 
                        database=database_info["database_id"],
                        credentials=credentials
                    )
                
                collections = list(db_client.collections())
                database_info["collections_count"] = len(collections)
                database_info["collections"] = [col.id for col in collections[:10]]  # First 10 collections
                
            except Exception as e:
                database_info["collections_count"] = "Unable to access"
                database_info["collections"] = []
                database_info["access_note"] = f"Collection access failed: {str(e)}"
            
            db_list.append(database_info)
        
        return {
            "status": "success",
            "project_id": project_id,
            "database_count": len(db_list),
            "databases": db_list,
            "resource_type": "firestore_databases"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list Firestore databases: {str(e)}",
            "resource_type": "firestore_databases",
            "error_type": str(type(e).__name__)
        }
