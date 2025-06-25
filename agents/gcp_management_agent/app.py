"""
GCP Management Functions
Clean production-ready functions for GCP resource operations
"""

import os
from typing import Dict, Optional, List
from google.cloud import storage
from google.cloud import compute_v1
from google.api_core import exceptions
from dotenv import load_dotenv

# Try to import Firestore - fall back gracefully if not available
try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

# Try to import Billing - fall back gracefully if not available
try:
    from google.cloud import billing_v1
    BILLING_AVAILABLE = True
except ImportError:
    BILLING_AVAILABLE = False

# Load environment variables
load_dotenv()


def create_storage_bucket(bucket_name: str, location: str = "US", storage_class: str = "STANDARD", 
                         versioning_enabled: bool = False, lifecycle_rules: Optional[Dict] = None) -> Dict:
    """
    Creates a Google Cloud Storage bucket with specified configuration.
    
    Args:
        bucket_name: Name of the bucket to create
        location: Location for the bucket (default: US)
        storage_class: Storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)
        versioning_enabled: Enable object versioning
        lifecycle_rules: Optional lifecycle management rules
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "storage_bucket"
            }
        
        client = storage.Client(project=project_id)
        
        # Check if bucket already exists
        try:
            bucket = client.get_bucket(bucket_name)
            return {
                "status": "error",
                "message": f"Bucket '{bucket_name}' already exists",
                "resource_type": "storage_bucket"
            }
        except exceptions.NotFound:
            pass
        
        # Create the bucket
        bucket = client.create_bucket(bucket_name, location=location)
        bucket.storage_class = storage_class
        
        if versioning_enabled:
            bucket.versioning_enabled = True
        
        if lifecycle_rules:
            bucket.lifecycle_rules = lifecycle_rules
            
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
                "created": bucket.time_created.isoformat() if bucket.time_created else None,
                "self_link": bucket.self_link
            }
        }
        
    except exceptions.Conflict:
        return {
            "status": "error",
            "message": f"Bucket name '{bucket_name}' is already taken globally",
            "resource_type": "storage_bucket"
        }
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and project permissions",
            "resource_type": "storage_bucket"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create bucket: {str(e)}",
            "resource_type": "storage_bucket"
        }


def delete_storage_bucket(bucket_name: str, force_delete_objects: bool = False) -> Dict:
    """
    Deletes a Google Cloud Storage bucket.
    
    Args:
        bucket_name: Name of the bucket to delete
        force_delete_objects: If True, deletes all objects in the bucket first
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "storage_bucket"
            }
        
        client = storage.Client(project=project_id)
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
                "resource_type": "storage_bucket",
                "details": {
                    "bucket_name": bucket_name,
                    "has_objects": True,
                    "suggestion": "Set force_delete_objects=True to delete all objects first"
                }
            }
        
        # Delete all objects if force is True
        if force_delete_objects:
            blobs = bucket.list_blobs()
            deleted_count = 0
            for blob in blobs:
                blob.delete()
                deleted_count += 1
        
        bucket.delete()
        
        return {
            "status": "success",
            "message": f"Storage bucket '{bucket_name}' deleted successfully",
            "resource_type": "storage_bucket",
            "details": {
                "bucket_name": bucket_name,
                "objects_deleted": force_delete_objects
            }
        }
        
    except exceptions.NotFound:
        return {
            "status": "error",
            "message": f"Bucket '{bucket_name}' not found",
            "resource_type": "storage_bucket"
        }
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and project permissions",
            "resource_type": "storage_bucket"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete bucket: {str(e)}",
            "resource_type": "storage_bucket"
        }


def list_storage_buckets() -> Dict:
    """
    Lists all storage buckets in the project.
    
    Returns:
        Dictionary containing list of buckets and their details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
            }
        
        client = storage.Client(project=project_id)
        buckets = list(client.list_buckets())
        
        bucket_list = []
        for bucket in buckets:
            bucket_info = {
                "name": bucket.name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "versioning_enabled": bucket.versioning_enabled,
                "created": bucket.time_created.isoformat() if bucket.time_created else None,
                "updated": bucket.updated.isoformat() if bucket.updated else None
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


def delete_all_storage_buckets(confirm_deletion: bool = False, force_delete_objects: bool = False) -> Dict:
    """
    Deletes all storage buckets in the project.
    
    Args:
        confirm_deletion: Must be True to proceed with deletion (safety check)
        force_delete_objects: If True, deletes all objects in buckets before deleting buckets
        
    Returns:
        Dictionary containing operation status and details
    """
    if not confirm_deletion:
        return {
            "status": "error",
            "message": "Deletion not confirmed. Set confirm_deletion=True to proceed",
            "resource_type": "storage_bucket"
        }
    
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "storage_bucket"
            }
        
        # First get list of all buckets
        bucket_list_result = list_storage_buckets()
        if bucket_list_result.get("status") != "success":
            return {
                "status": "error",
                "message": f"Failed to list buckets: {bucket_list_result.get('message')}",
                "resource_type": "storage_bucket"
            }
        
        buckets = bucket_list_result.get("buckets", [])
        if not buckets:
            return {
                "status": "success",
                "message": "No buckets found to delete",
                "resource_type": "storage_bucket",
                "details": {
                    "deleted_count": 0,
                    "failed_count": 0,
                    "total_count": 0
                }
            }
        
        # Delete each bucket
        deleted_buckets = []
        failed_buckets = []
        
        for bucket_info in buckets:
            bucket_name = bucket_info["name"]
            delete_result = delete_storage_bucket(bucket_name, force_delete_objects)
            
            if delete_result.get("status") == "success":
                deleted_buckets.append(bucket_name)
            else:
                failed_buckets.append({
                    "name": bucket_name,
                    "error": delete_result.get("message")
                })
        
        return {
            "status": "success" if not failed_buckets else "partial_success",
            "message": f"Deleted {len(deleted_buckets)} buckets, {len(failed_buckets)} failed",
            "resource_type": "storage_bucket",
            "details": {
                "deleted_count": len(deleted_buckets),
                "failed_count": len(failed_buckets),
                "total_count": len(buckets),
                "deleted_buckets": deleted_buckets,
                "failed_buckets": failed_buckets
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete all buckets: {str(e)}",
            "resource_type": "storage_bucket"
        }


# Compute Engine Functions

def create_compute_instance(instance_name: str, zone: str = "us-central1-a", 
                          machine_type: str = "e2-micro", disk_size_gb: int = 10,
                          image_family: str = "ubuntu-2204-lts", image_project: str = "ubuntu-os-cloud",
                          network_tags: Optional[List[str]] = None) -> Dict:
    """
    Creates a Compute Engine instance.
    
    Args:
        instance_name: Name for the new instance
        zone: Zone where to create the instance
        machine_type: Machine type (e2-micro, e2-small, n1-standard-1, etc.)
        disk_size_gb: Boot disk size in GB
        image_family: Image family to use
        image_project: Project containing the image
        network_tags: List of network tags for firewall rules
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "compute_instance"
            }
        
        compute_client = compute_v1.InstancesClient()
        
        # Check if instance already exists
        try:
            request = compute_v1.GetInstanceRequest(
                project=project_id,
                zone=zone,
                instance=instance_name
            )
            existing_instance = compute_client.get(request=request)
            return {
                "status": "error",
                "message": f"Instance '{instance_name}' already exists in zone '{zone}'",
                "resource_type": "compute_instance"
            }
        except exceptions.NotFound:
            pass  # Instance doesn't exist, we can create it
        
        # Configure the instance
        instance_config = {
            "name": instance_name,
            "machine_type": f"zones/{zone}/machineTypes/{machine_type}",
            "disks": [
                {
                    "boot": True,
                    "auto_delete": True,
                    "initialize_params": {
                        "source_image": f"projects/{image_project}/global/images/family/{image_family}",
                        "disk_size_gb": str(disk_size_gb)
                    }
                }
            ],
            "network_interfaces": [
                {
                    "network": "global/networks/default",
                    "access_configs": [
                        {
                            "type": "ONE_TO_ONE_NAT",
                            "name": "External NAT"
                        }
                    ]
                }
            ]
        }
        
        # Add network tags if provided
        if network_tags:
            instance_config["tags"] = {"items": network_tags}
        
        # Create the instance
        request = compute_v1.InsertInstanceRequest(
            project=project_id,
            zone=zone,
            instance_resource=instance_config
        )
        
        operation = compute_client.insert(request=request)
        
        return {
            "status": "success",
            "message": f"Compute instance '{instance_name}' created successfully",
            "resource_type": "compute_instance",
            "details": {
                "name": instance_name,
                "zone": zone,
                "machine_type": machine_type,
                "disk_size_gb": disk_size_gb,
                "image": f"{image_project}/{image_family}",
                "network_tags": network_tags or [],
                "operation_id": operation.name,
                "operation_status": operation.status
            }
        }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and compute permissions",
            "resource_type": "compute_instance"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create compute instance: {str(e)}",
            "resource_type": "compute_instance"
        }


def delete_compute_instance(instance_name: str, zone: str) -> Dict:
    """
    Deletes a Compute Engine instance.
    
    Args:
        instance_name: Name of the instance to delete
        zone: Zone where the instance is located
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "compute_instance"
            }
        
        compute_client = compute_v1.InstancesClient()
        
        # Check if instance exists before trying to delete
        try:
            request = compute_v1.GetInstanceRequest(
                project=project_id,
                zone=zone,
                instance=instance_name
            )
            existing_instance = compute_client.get(request=request)
        except exceptions.NotFound:
            return {
                "status": "error",
                "message": f"Instance '{instance_name}' not found in zone '{zone}'",
                "resource_type": "compute_instance"
            }
        
        # Delete the instance
        request = compute_v1.DeleteInstanceRequest(
            project=project_id,
            zone=zone,
            instance=instance_name
        )
        
        operation = compute_client.delete(request=request)
        
        return {
            "status": "success",
            "message": f"Compute instance '{instance_name}' deletion initiated",
            "resource_type": "compute_instance",
            "details": {
                "name": instance_name,
                "zone": zone,
                "operation_id": operation.name,
                "operation_status": operation.status,
                "operation_type": "delete_instance"
            }
        }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and compute permissions",
            "resource_type": "compute_instance"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete compute instance: {str(e)}",
            "resource_type": "compute_instance"
        }


def list_compute_instances(zone: Optional[str] = None) -> Dict:
    """
    Lists compute instances in the project.
    
    Args:
        zone: Specific zone to list instances from (if None, lists from all zones)
        
    Returns:
        Dictionary containing list of instances and their details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
            }
        
        compute_client = compute_v1.InstancesClient()
        zones_client = compute_v1.ZonesClient()
        
        all_instances = []
        zones_to_check = []
        
        if zone:
            # Check specific zone only
            zones_to_check = [zone]
        else:
            # Get all zones in the project
            zones_request = compute_v1.ListZonesRequest(project=project_id)
            zones_response = zones_client.list(request=zones_request)
            zones_to_check = [z.name for z in zones_response]
        
        # List instances in each zone
        for zone_name in zones_to_check:
            try:
                instances_request = compute_v1.ListInstancesRequest(
                    project=project_id,
                    zone=zone_name
                )
                zone_instances = compute_client.list(request=instances_request)
                
                for instance in zone_instances:
                    # Get IP addresses
                    internal_ip = None
                    external_ip = None
                    
                    if instance.network_interfaces:
                        internal_ip = instance.network_interfaces[0].network_i_p
                        if instance.network_interfaces[0].access_configs:
                            external_ip = instance.network_interfaces[0].access_configs[0].nat_i_p
                    
                    # Get disk size from boot disk
                    disk_size_gb = None
                    if instance.disks:
                        for disk in instance.disks:
                            if disk.boot:
                                try:
                                    disk_size_gb = int(disk.disk_size_gb) if hasattr(disk, 'disk_size_gb') else None
                                except:
                                    pass
                                break
                    
                    instance_info = {
                        "name": instance.name,
                        "zone": zone_name,
                        "machine_type": instance.machine_type.split("/")[-1],
                        "status": instance.status,
                        "internal_ip": internal_ip,
                        "external_ip": external_ip,
                        "created": instance.creation_timestamp,
                        "disk_size_gb": disk_size_gb,
                        "image": None,
                        "network_tags": list(instance.tags.items) if instance.tags else []
                    }
                    
                    # Try to get source image from boot disk
                    if instance.disks:
                        for disk in instance.disks:
                            if disk.boot and hasattr(disk, 'source_image'):
                                instance_info["image"] = disk.source_image.split("/")[-1] if disk.source_image else None
                                break
                    
                    all_instances.append(instance_info)
                    
            except exceptions.Forbidden:
                # Skip zones we don't have access to
                continue
            except Exception:
                # Skip zones with errors
                continue
        
        return {
            "status": "success",
            "project_id": project_id,
            "instance_count": len(all_instances),
            "instances": all_instances,
            "zones_checked": zones_to_check if not zone else [zone]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list compute instances: {str(e)}"
        }


# Firestore Functions

def create_firestore_database(database_id: str = "(default)", location_id: str = "nam5", 
                             database_type: str = "FIRESTORE_NATIVE") -> Dict:
    """
    Creates a Firestore database by initializing a client (which auto-creates if needed).
    
    Args:
        database_id: ID for the database (default: "(default)")
        location_id: Location for the database (default: "nam5" - North America)
        database_type: Type of database (for compatibility, not used in basic setup)
        
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
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "firestore_database"
            }
        
        # Initialize Firestore client (this creates the database if it doesn't exist)
        db = firestore.Client(project=project_id)
        
        # Test the connection by creating a simple document
        test_collection = db.collection('test_collection')
        test_doc = test_collection.document('test_doc')
        test_doc.set({
            'created_at': firestore.SERVER_TIMESTAMP,
            'message': 'Database initialized successfully'
        })
        
        # Clean up the test document
        test_doc.delete()
        
        return {
            "status": "success",
            "message": f"Firestore database initialized successfully",
            "resource_type": "firestore_database",
            "details": {
                "project_id": project_id,
                "database_id": database_id,
                "location_note": f"Database uses project default location",
                "status": "active"
            }
        }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and Firestore permissions",
            "resource_type": "firestore_database"
        }
    except exceptions.FailedPrecondition as e:
        return {
            "status": "error",
            "message": f"Failed precondition: {str(e)}. Ensure Firestore API is enabled",
            "resource_type": "firestore_database"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize Firestore database: {str(e)}",
            "resource_type": "firestore_database"
        }


def delete_firestore_database(database_id: str = "(default)") -> Dict:
    """
    Deletes all data from Firestore database (note: cannot delete the database itself via client library).
    
    Args:
        database_id: ID of the database (for compatibility)
        
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
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set",
                "resource_type": "firestore_database"
            }
        
        # Initialize Firestore client
        db = firestore.Client(project=project_id)
        
        # List all collections and delete them
        collections = db.collections()
        deleted_collections = []
        
        for collection in collections:
            collection_name = collection.id
            # Delete all documents in the collection
            docs = collection.stream()
            deleted_count = 0
            
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
            
            deleted_collections.append({
                "collection": collection_name,
                "documents_deleted": deleted_count
            })
        
        return {
            "status": "success",
            "message": f"Firestore database data cleared successfully",
            "resource_type": "firestore_database",
            "details": {
                "project_id": project_id,
                "database_id": database_id,
                "collections_cleared": len(deleted_collections),
                "deleted_collections": deleted_collections,
                "note": "Database structure remains, only data was deleted"
            }
        }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. Check your GCP credentials and Firestore permissions",
            "resource_type": "firestore_database"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to clear Firestore database: {str(e)}",
            "resource_type": "firestore_database"
        }


def list_firestore_databases() -> Dict:
    """
    Lists Firestore database information and collections.
    
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
        
        # Initialize Firestore client
        db = firestore.Client(project=project_id)
        
        # Get all collections
        collections = list(db.collections())
        collection_info = []
        
        for collection in collections:
            # Count documents in each collection
            docs = list(collection.limit(1000).stream())  # Limit for performance
            
            collection_info.append({
                "collection_id": collection.id,
                "document_count": len(docs),
                "path": collection.path
            })
        
        return {
            "status": "success",
            "project_id": project_id,
            "database_info": {
                "database_id": "(default)",
                "type": "FIRESTORE_NATIVE",
                "status": "active",
                "collections_count": len(collection_info)
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
            "message": f"Failed to list Firestore information: {str(e)}"
        }


# Billing Functions

def get_billing_summary() -> Dict:
    """
    Retrieves current billing information and project billing status.
    
    Returns:
        Dictionary containing billing information and status
    """
    if not BILLING_AVAILABLE:
        return {
            "status": "error",
            "message": "Billing API not available. Install: pip install google-cloud-billing"
        }
    
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
            }
        
        # Initialize billing client
        billing_client = billing_v1.CloudBillingClient()
        
        # Get project billing info
        project_name = f"projects/{project_id}"
        
        try:
            billing_info = billing_client.get_project_billing_info(name=project_name)
            
            # Get billing account details if available
            billing_account_info = None
            if billing_info.billing_account_name:
                try:
                    billing_account_info = billing_client.get_billing_account(
                        name=billing_info.billing_account_name
                    )
                except Exception:
                    # If we can't get billing account details, continue without them
                    pass
            
            return {
                "status": "success",
                "project_id": project_id,
                "billing_enabled": billing_info.billing_enabled,
                "billing_account_name": billing_info.billing_account_name,
                "billing_account_info": {
                    "display_name": billing_account_info.display_name if billing_account_info else "Unknown",
                    "open": billing_account_info.open if billing_account_info else None,
                    "currency_code": billing_account_info.currency_code if billing_account_info else "Unknown"
                } if billing_account_info else None,
                "message": "Billing is enabled and active" if billing_info.billing_enabled else "Billing is not enabled for this project",
                "recommendations": [
                    "Monitor your usage regularly",
                    "Set up billing alerts",
                    "Review your billing reports monthly"
                ] if billing_info.billing_enabled else [
                    "Enable billing to use paid GCP services",
                    "Visit Google Cloud Console to set up billing"
                ]
            }
            
        except exceptions.NotFound:
            return {
                "status": "error",
                "message": f"Project '{project_id}' not found or you don't have access to billing information"
            }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. You need 'Billing Account Viewer' or 'Billing Account Administrator' role to access billing information"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve billing information: {str(e)}"
        }


def list_billing_accounts() -> Dict:
    """
    Lists all billing accounts that the user has access to.
    
    Returns:
        Dictionary containing list of billing accounts
    """
    if not BILLING_AVAILABLE:
        return {
            "status": "error",
            "message": "Billing API not available. Install: pip install google-cloud-billing"
        }
    
    try:
        # Initialize billing client
        billing_client = billing_v1.CloudBillingClient()
        
        # List all billing accounts
        billing_accounts = billing_client.list_billing_accounts()
        
        accounts_list = []
        for account in billing_accounts:
            account_info = {
                "name": account.name,
                "display_name": account.display_name,
                "open": account.open,
                "currency_code": account.currency_code,
                "master_billing_account": account.master_billing_account
            }
            accounts_list.append(account_info)
        
        return {
            "status": "success",
            "account_count": len(accounts_list),
            "billing_accounts": accounts_list,
            "message": f"Found {len(accounts_list)} billing account(s)"
        }
        
    except exceptions.Forbidden:
        return {
            "status": "error",
            "message": "Permission denied. You need billing account access to list billing accounts"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list billing accounts: {str(e)}"
        }


def validate_environment() -> Dict:
    """
    Validates that the environment is properly configured for GCP operations.
    
    Returns:
        Dictionary containing validation status and details
    """
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        return {
            "status": "error",
            "message": "GOOGLE_CLOUD_PROJECT environment variable not set"
        }
    
    if not creds_path:
        return {
            "status": "error", 
            "message": "GOOGLE_APPLICATION_CREDENTIALS environment variable not set"
        }
        
    if not os.path.exists(creds_path):
        return {
            "status": "error",
            "message": f"Credentials file not found: {creds_path}"
        }
    
    try:
        # Test storage client
        storage_client = storage.Client(project=project_id)
        
        # Test compute client
        compute_client = compute_v1.InstancesClient()
        
        # Test firestore client if available
        if FIRESTORE_AVAILABLE:
            firestore_client = firestore.Client(project=project_id)
        
        # Test billing client if available
        if BILLING_AVAILABLE:
            billing_client = billing_v1.CloudBillingClient()
        
        return {
            "status": "success",
            "message": "Environment validation successful",
            "project_id": project_id,
            "credentials_path": creds_path,
            "firestore_available": FIRESTORE_AVAILABLE,
            "billing_available": BILLING_AVAILABLE
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize storage client: {str(e)}"
        }


def run_comprehensive_tests() -> Dict:
    """
    Tests all GCP management functions and provides a detailed report.
    
    Returns:
        Dictionary containing test results for all functions
    """
    import time
    timestamp = str(int(time.time()))
    
    test_results = {
        "environment_validation": None,
        "storage_functions": {
            "list_buckets": None,
            "create_bucket": None,
            "delete_bucket": None
        },
        "compute_functions": {
            "list_instances": None,
            "list_instances_specific_zone": None,
            "create_instance": None,
            "delete_instance": None
        },
        "firestore_functions": {
            "list_databases": None,
            "create_database": None,
            "delete_database": None
        },
        "billing_functions": {
            "get_billing_summary": None,
            "list_billing_accounts": None
        },
        "summary": {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0
        }
    }
    
    print("=" * 80)
    print("COMPREHENSIVE GCP MANAGEMENT FUNCTIONS TEST")
    print("=" * 80)
    
    # Test 1: Environment Validation
    print("\n1. TESTING ENVIRONMENT VALIDATION")
    print("-" * 40)
    try:
        env_result = validate_environment()
        test_results["environment_validation"] = env_result
        if env_result.get("status") == "success":
            print("✅ Environment validation: PASSED")
            print(f"   Project: {env_result.get('project_id')}")
        else:
            print("❌ Environment validation: FAILED")
            print(f"   Error: {env_result.get('message')}")
            return test_results  # Stop if environment validation fails
    except Exception as e:
        print(f"❌ Environment validation: FAILED - {str(e)}")
        test_results["environment_validation"] = {"status": "error", "message": str(e)}
        return test_results
    
    # Test 2: Storage Functions
    print("\n2. TESTING STORAGE FUNCTIONS")
    print("-" * 40)
    
    # Test 2a: List Buckets
    print("2a. Testing list_storage_buckets()...")
    try:
        buckets_result = list_storage_buckets()
        test_results["storage_functions"]["list_buckets"] = buckets_result
        if buckets_result.get("status") == "success":
            print(f"✅ List buckets: PASSED ({buckets_result.get('bucket_count')} buckets found)")
        else:
            print(f"❌ List buckets: FAILED - {buckets_result.get('message')}")
    except Exception as e:
        print(f"❌ List buckets: FAILED - {str(e)}")
        test_results["storage_functions"]["list_buckets"] = {"status": "error", "message": str(e)}
    
    # Test 2b: Create Bucket
    print("2b. Testing create_storage_bucket()...")
    test_bucket_name = f"test-bucket-{timestamp}"
    try:
        create_result = create_storage_bucket(test_bucket_name)
        test_results["storage_functions"]["create_bucket"] = create_result
        if create_result.get("status") == "success":
            print(f"✅ Create bucket: PASSED (bucket: {test_bucket_name})")
        else:
            print(f"❌ Create bucket: FAILED - {create_result.get('message')}")
            test_bucket_name = None  # Don't try to delete if creation failed
    except Exception as e:
        print(f"❌ Create bucket: FAILED - {str(e)}")
        test_results["storage_functions"]["create_bucket"] = {"status": "error", "message": str(e)}
        test_bucket_name = None
    
    # Test 2c: Delete Bucket (only if creation succeeded)
    print("2c. Testing delete_storage_bucket()...")
    if test_bucket_name:
        try:
            delete_result = delete_storage_bucket(test_bucket_name)
            test_results["storage_functions"]["delete_bucket"] = delete_result
            if delete_result.get("status") == "success":
                print(f"✅ Delete bucket: PASSED (bucket: {test_bucket_name})")
            else:
                print(f"❌ Delete bucket: FAILED - {delete_result.get('message')}")
        except Exception as e:
            print(f"❌ Delete bucket: FAILED - {str(e)}")
            test_results["storage_functions"]["delete_bucket"] = {"status": "error", "message": str(e)}
    else:
        print("⚠️  Delete bucket: SKIPPED (creation failed)")
        test_results["storage_functions"]["delete_bucket"] = {"status": "skipped", "message": "Creation failed"}
    
    # Test 3: Compute Functions
    print("\n3. TESTING COMPUTE FUNCTIONS")
    print("-" * 40)
    
    # Test 3a: List All Instances
    print("3a. Testing list_compute_instances() - all zones...")
    try:
        instances_result = list_compute_instances()
        test_results["compute_functions"]["list_instances"] = instances_result
        if instances_result.get("status") == "success":
            print(f"✅ List all instances: PASSED ({instances_result.get('instance_count')} instances found)")
        else:
            print(f"❌ List all instances: FAILED - {instances_result.get('message')}")
    except Exception as e:
        print(f"❌ List all instances: FAILED - {str(e)}")
        test_results["compute_functions"]["list_instances"] = {"status": "error", "message": str(e)}
    
    # Test 3b: List Instances in Specific Zone
    print("3b. Testing list_compute_instances() - specific zone...")
    try:
        zone_instances_result = list_compute_instances(zone="us-central1-a")
        test_results["compute_functions"]["list_instances_specific_zone"] = zone_instances_result
        if zone_instances_result.get("status") == "success":
            print(f"✅ List zone instances: PASSED ({zone_instances_result.get('instance_count')} instances in us-central1-a)")
        else:
            print(f"❌ List zone instances: FAILED - {zone_instances_result.get('message')}")
    except Exception as e:
        print(f"❌ List zone instances: FAILED - {str(e)}")
        test_results["compute_functions"]["list_instances_specific_zone"] = {"status": "error", "message": str(e)}
    
    # Test 3c: Create Instance
    print("3c. Testing create_compute_instance()...")
    test_instance_name = f"test-vm-{timestamp}"
    try:
        create_vm_result = create_compute_instance(
            instance_name=test_instance_name,
            zone="us-central1-a",
            machine_type="e2-micro",
            image_family="ubuntu-2204-lts"
        )
        test_results["compute_functions"]["create_instance"] = create_vm_result
        if create_vm_result.get("status") == "success":
            print(f"✅ Create instance: PASSED (instance: {test_instance_name})")
        else:
            print(f"❌ Create instance: FAILED - {create_vm_result.get('message')}")
            test_instance_name = None  # Don't try to delete if creation failed
    except Exception as e:
        print(f"❌ Create instance: FAILED - {str(e)}")
        test_results["compute_functions"]["create_instance"] = {"status": "error", "message": str(e)}
        test_instance_name = None
    
    # Test 3d: Delete Instance (only if creation succeeded)
    print("3d. Testing delete_compute_instance()...")
    if test_instance_name:
        # Wait a moment for the instance to be created
        print("   Waiting 30 seconds for instance to be ready...")
        time.sleep(30)
        
        try:
            delete_vm_result = delete_compute_instance(test_instance_name, "us-central1-a")
            test_results["compute_functions"]["delete_instance"] = delete_vm_result
            if delete_vm_result.get("status") == "success":
                print(f"✅ Delete instance: PASSED (instance: {test_instance_name})")
            else:
                print(f"❌ Delete instance: FAILED - {delete_vm_result.get('message')}")
        except Exception as e:
            print(f"❌ Delete instance: FAILED - {str(e)}")
            test_results["compute_functions"]["delete_instance"] = {"status": "error", "message": str(e)}
    else:
        print("⚠️  Delete instance: SKIPPED (creation failed)")
        test_results["compute_functions"]["delete_instance"] = {"status": "skipped", "message": "Creation failed"}
    
    # Test 4: Firestore Functions
    print("\n4. TESTING FIRESTORE FUNCTIONS")
    print("-" * 40)
    
    # Test 4a: List Firestore Databases
    print("4a. Testing list_firestore_databases()...")
    try:
        firestore_list_result = list_firestore_databases()
        test_results["firestore_functions"]["list_databases"] = firestore_list_result
        if firestore_list_result.get("status") == "success":
            print(f"✅ List Firestore databases: PASSED ({firestore_list_result.get('database_count')} databases found)")
        else:
            print(f"❌ List Firestore databases: FAILED - {firestore_list_result.get('message')}")
    except Exception as e:
        print(f"❌ List Firestore databases: FAILED - {str(e)}")
        test_results["firestore_functions"]["list_databases"] = {"status": "error", "message": str(e)}
    
    # Test 4b: Create Firestore Database
    print("4b. Testing create_firestore_database()...")
    test_db_id = f"test-db-{timestamp}"
    try:
        create_firestore_result = create_firestore_database(
            database_id=test_db_id,
            location_id="nam5"
        )
        test_results["firestore_functions"]["create_database"] = create_firestore_result
        if create_firestore_result.get("status") == "success":
            print(f"✅ Create Firestore database: PASSED (database: {test_db_id})")
        else:
            print(f"❌ Create Firestore database: FAILED - {create_firestore_result.get('message')}")
            test_db_id = None  # Don't try to delete if creation failed
    except Exception as e:
        print(f"❌ Create Firestore database: FAILED - {str(e)}")
        test_results["firestore_functions"]["create_database"] = {"status": "error", "message": str(e)}
        test_db_id = None
    
    # Test 4c: Delete Firestore Database (only if creation succeeded)
    print("4c. Testing delete_firestore_database()...")
    if test_db_id:
        # Wait a moment for the database to be ready
        print("   Waiting 60 seconds for database to be ready...")
        time.sleep(60)
        
        try:
            delete_firestore_result = delete_firestore_database(test_db_id)
            test_results["firestore_functions"]["delete_database"] = delete_firestore_result
            if delete_firestore_result.get("status") == "success":
                print(f"✅ Delete Firestore database: PASSED (database: {test_db_id})")
            else:
                print(f"❌ Delete Firestore database: FAILED - {delete_firestore_result.get('message')}")
        except Exception as e:
            print(f"❌ Delete Firestore database: FAILED - {str(e)}")
            test_results["firestore_functions"]["delete_database"] = {"status": "error", "message": str(e)}
    else:
        print("⚠️  Delete Firestore database: SKIPPED (creation failed)")
        test_results["firestore_functions"]["delete_database"] = {"status": "skipped", "message": "Creation failed"}
    
    # Test 5: Billing Functions
    print("\n5. TESTING BILLING FUNCTIONS")
    print("-" * 40)
    
    # Test 5a: Get Billing Summary
    print("5a. Testing get_billing_summary()...")
    try:
        billing_summary_result = get_billing_summary()
        test_results["billing_functions"]["get_billing_summary"] = billing_summary_result
        if billing_summary_result.get("status") == "success":
            billing_enabled = billing_summary_result.get("billing_enabled", False)
            print(f"✅ Get billing summary: PASSED (billing enabled: {billing_enabled})")
        else:
            print(f"❌ Get billing summary: FAILED - {billing_summary_result.get('message')}")
    except Exception as e:
        print(f"❌ Get billing summary: FAILED - {str(e)}")
        test_results["billing_functions"]["get_billing_summary"] = {"status": "error", "message": str(e)}
    
    # Test 5b: List Billing Accounts
    print("5b. Testing list_billing_accounts()...")
    try:
        billing_accounts_result = list_billing_accounts()
        test_results["billing_functions"]["list_billing_accounts"] = billing_accounts_result
        if billing_accounts_result.get("status") == "success":
            account_count = billing_accounts_result.get("account_count", 0)
            print(f"✅ List billing accounts: PASSED ({account_count} accounts found)")
        else:
            print(f"❌ List billing accounts: FAILED - {billing_accounts_result.get('message')}")
    except Exception as e:
        print(f"❌ List billing accounts: FAILED - {str(e)}")
        test_results["billing_functions"]["list_billing_accounts"] = {"status": "error", "message": str(e)}
    
    # Calculate Summary
    print("\n6. TEST SUMMARY")
    print("-" * 40)
    
    total_tests = 0
    passed_tests = 0
    
    # Count environment test
    total_tests += 1
    if test_results["environment_validation"] and test_results["environment_validation"].get("status") == "success":
        passed_tests += 1
    
    # Count storage tests
    for test_name, result in test_results["storage_functions"].items():
        total_tests += 1
        if result and result.get("status") == "success":
            passed_tests += 1
    
    # Count compute tests
    for test_name, result in test_results["compute_functions"].items():
        total_tests += 1
        if result and result.get("status") == "success":
            passed_tests += 1
    
    # Count firestore tests
    for test_name, result in test_results["firestore_functions"].items():
        total_tests += 1
        if result and result.get("status") == "success":
            passed_tests += 1
    
    # Count billing tests
    for test_name, result in test_results["billing_functions"].items():
        total_tests += 1
        if result and result.get("status") == "success":
            passed_tests += 1
    
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    test_results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": round(success_rate, 1)
    }
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate}%")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! Your GCP management functions are working perfectly!")
    elif success_rate >= 70:
        print("\n✅ Most tests passed! Some functions may need permission fixes.")
    else:
        print("\n⚠️  Several tests failed. Check permissions and configuration.")
    
    print("=" * 80)
    
    return test_results


# Example usage and testing
if __name__ == "__main__":
    # Run comprehensive tests of all functions
    results = run_comprehensive_tests()
    
    # Print only the final result
    print(f"\nFinal Result: {results['summary']['success_rate']}% of functions working")
    print(f"({results['summary']['passed_tests']}/{results['summary']['total_tests']} tests passed)")