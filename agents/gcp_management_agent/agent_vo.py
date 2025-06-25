"""
MIT License

Copyright (c) 2024 Ngoga Alexis

GCP Resource Management Agent using Google ADK.
This agent handles provisioning and deprovisioning of GCP resources.
Part of a multi-agent system for GCP management.
"""

from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime, timedelta
from google.adk.agents import Agent
from google.cloud import storage
from google.cloud import billing_v1
from google.cloud import compute_v1
from google.cloud import container_v1
from google.cloud import sql_v1
from google.cloud import functions_v1
from google.cloud import resourcemanager_v3
from google.api_core import exceptions
from dotenv import load_dotenv

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
            pass  # Bucket doesn't exist, we can create it
        
        # Create the bucket
        bucket = client.create_bucket(bucket_name, location=location)
        bucket.storage_class = storage_class
        
        # Configure versioning if requested
        if versioning_enabled:
            bucket.versioning_enabled = True
        
        # Apply lifecycle rules if provided
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

def create_compute_instance(instance_name: str, zone: str = "us-central1-a", 
                          machine_type: str = "e2-micro", disk_size_gb: int = 10,
                          image_family: str = "ubuntu-2004-lts", image_project: str = "ubuntu-os-cloud",
                          network_tags: Optional[List[str]] = None, startup_script: Optional[str] = None) -> Dict:
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
        startup_script: Optional startup script to run on first boot
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        compute_client = compute_v1.InstancesClient()
        
        # Prepare startup script metadata if provided
        metadata_items = []
        if startup_script:
            metadata_items.append({
                "key": "startup-script",
                "value": startup_script
            })
        
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
        
        # Add metadata if startup script provided
        if metadata_items:
            instance_config["metadata"] = {"items": metadata_items}
        
        request = compute_v1.InsertInstanceRequest(
            project=project_id,
            zone=zone,
            instance_resource=instance_config
        )
        
        operation = compute_client.insert(request=request)
        
        return {
            "status": "success",
            "message": f"Compute instance '{instance_name}' creation initiated",
            "resource_type": "compute_instance",
            "details": {
                "name": instance_name,
                "zone": zone,
                "machine_type": machine_type,
                "disk_size_gb": disk_size_gb,
                "image": f"{image_project}/{image_family}",
                "operation_id": operation.name,
                "operation_status": operation.status
            }
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
        compute_client = compute_v1.InstancesClient()
        
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
                "operation_status": operation.status
            }
        }
    except exceptions.NotFound:
        return {
            "status": "error",
            "message": f"Instance '{instance_name}' not found in zone '{zone}'",
            "resource_type": "compute_instance"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete compute instance: {str(e)}",
            "resource_type": "compute_instance"
        }

def create_cloud_sql_instance(instance_name: str, database_version: str = "MYSQL_8_0",
                            tier: str = "db-f1-micro", region: str = "us-central1",
                            root_password: str = None, authorized_networks: Optional[List[str]] = None) -> Dict:
    """
    Creates a Cloud SQL instance.
    
    Args:
        instance_name: Name for the SQL instance
        database_version: Database version (MYSQL_8_0, POSTGRES_13, etc.)
        tier: Machine tier (db-f1-micro, db-n1-standard-1, etc.)
        region: Region for the instance
        root_password: Root password (will be auto-generated if not provided)
        authorized_networks: List of authorized network CIDR blocks
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        sql_client = sql_v1.SqlInstancesServiceClient()
        
        # Configure the instance
        instance_config = {
            "name": instance_name,
            "database_version": database_version,
            "region": region,
            "settings": {
                "tier": tier,
                "backup_configuration": {
                    "enabled": True,
                    "start_time": "03:00"
                },
                "ip_configuration": {
                    "ipv4_enabled": True
                }
            }
        }
        
        # Add authorized networks if provided
        if authorized_networks:
            instance_config["settings"]["ip_configuration"]["authorized_networks"] = [
                {"value": network} for network in authorized_networks
            ]
        
        request = sql_v1.SqlInstancesInsertRequest(
            project=project_id,
            body=instance_config
        )
        
        operation = sql_client.insert(request=request)
        
        return {
            "status": "success",
            "message": f"Cloud SQL instance '{instance_name}' creation initiated",
            "resource_type": "cloud_sql_instance",
            "details": {
                "name": instance_name,
                "database_version": database_version,
                "tier": tier,
                "region": region,
                "operation_id": operation.name
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create Cloud SQL instance: {str(e)}",
            "resource_type": "cloud_sql_instance"
        }

def delete_cloud_sql_instance(instance_name: str) -> Dict:
    """
    Deletes a Cloud SQL instance.
    
    Args:
        instance_name: Name of the SQL instance to delete
        
    Returns:
        Dictionary containing operation status and details
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        sql_client = sql_v1.SqlInstancesServiceClient()
        
        request = sql_v1.SqlInstancesDeleteRequest(
            project=project_id,
            instance=instance_name
        )
        
        operation = sql_client.delete(request=request)
        
        return {
            "status": "success",
            "message": f"Cloud SQL instance '{instance_name}' deletion initiated",
            "resource_type": "cloud_sql_instance",
            "details": {
                "name": instance_name,
                "operation_id": operation.name
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete Cloud SQL instance: {str(e)}",
            "resource_type": "cloud_sql_instance"
        }

def list_all_resources(resource_types: Optional[List[str]] = None) -> Dict:
    """
    Lists all resources in the project, optionally filtered by type.
    
    Args:
        resource_types: List of resource types to include (storage, compute, sql, etc.)
                       If None, lists all supported resource types
        
    Returns:
        Dictionary containing all resources organized by type
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        if resource_types is None:
            resource_types = ["storage", "compute", "sql"]
        
        all_resources = {}
        
        # List Storage Buckets
        if "storage" in resource_types:
            try:
                storage_client = storage.Client(project=project_id)
                buckets = list(storage_client.list_buckets())
                all_resources["storage_buckets"] = [
                    {
                        "name": bucket.name,
                        "location": bucket.location,
                        "storage_class": bucket.storage_class,
                        "versioning_enabled": bucket.versioning_enabled,
                        "created": bucket.time_created.isoformat() if bucket.time_created else None
                    } for bucket in buckets
                ]
            except Exception as e:
                all_resources["storage_buckets"] = {"error": str(e)}
        
        # List Compute Instances
        if "compute" in resource_types:
            try:
                compute_client = compute_v1.InstancesClient()
                zones_client = compute_v1.ZonesClient()
                
                # Get all zones in the project
                zones_request = compute_v1.ListZonesRequest(project=project_id)
                zones = zones_client.list(request=zones_request)
                
                instances = []
                for zone in zones:
                    try:
                        instances_request = compute_v1.ListInstancesRequest(
                            project=project_id,
                            zone=zone.name
                        )
                        zone_instances = compute_client.list(request=instances_request)
                        
                        for instance in zone_instances:
                            instances.append({
                                "name": instance.name,
                                "zone": zone.name,
                                "machine_type": instance.machine_type.split("/")[-1],
                                "status": instance.status,
                                "internal_ip": instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
                                "external_ip": instance.network_interfaces[0].access_configs[0].nat_i_p if instance.network_interfaces and instance.network_interfaces[0].access_configs else None,
                                "created": instance.creation_timestamp
                            })
                    except:
                        continue  # Skip zones with no access or instances
                
                all_resources["compute_instances"] = instances
            except Exception as e:
                all_resources["compute_instances"] = {"error": str(e)}
        
        # List Cloud SQL Instances
        if "sql" in resource_types:
            try:
                sql_client = sql_v1.SqlInstancesServiceClient()
                request = sql_v1.SqlInstancesListRequest(project=project_id)
                sql_instances = sql_client.list(request=request)
                
                all_resources["sql_instances"] = [
                    {
                        "name": instance.name,
                        "database_version": instance.database_version,
                        "region": instance.region,
                        "tier": instance.settings.tier,
                        "state": instance.state,
                        "ip_addresses": [
                            {"ip": ip.ip_address, "type": ip.type_} 
                            for ip in instance.ip_addresses
                        ]
                    } for instance in sql_instances.items
                ]
            except Exception as e:
                all_resources["sql_instances"] = {"error": str(e)}
        
        return {
            "status": "success",
            "project_id": project_id,
            "resources": all_resources,
            "resource_count": sum(
                len(resources) if isinstance(resources, list) else 0 
                for resources in all_resources.values()
            )
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list resources: {str(e)}"
        }

def get_billing_summary() -> Dict:
    """
    Retrieves current billing information and cost summary.
    
    Returns:
        Dictionary containing billing information
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        billing_client = billing_v1.CloudBillingClient()
        
        # Get project billing info
        project_name = f"projects/{project_id}"
        billing_info = billing_client.get_project_billing_info(name=project_name)
        
        # Note: Detailed cost breakdown requires Cloud Billing API with proper setup
        # This is a simplified version showing billing account status
        return {
            "status": "success",
            "project_id": project_id,
            "billing_enabled": billing_info.billing_enabled,
            "billing_account": billing_info.billing_account_name,
            "message": "Billing is active" if billing_info.billing_enabled else "Billing is not enabled"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve billing information: {str(e)}"
        }

def check_operation_status(operation_id: str, operation_type: str, zone: Optional[str] = None) -> Dict:
    """
    Checks the status of a long-running operation.
    
    Args:
        operation_id: The operation ID to check
        operation_type: Type of operation (compute, sql, etc.)
        zone: Zone for compute operations
        
    Returns:
        Dictionary containing operation status
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        if operation_type == "compute" and zone:
            compute_client = compute_v1.ZoneOperationsClient()
            request = compute_v1.GetZoneOperationRequest(
                project=project_id,
                zone=zone,
                operation=operation_id
            )
            operation = compute_client.get(request=request)
            
            return {
                "status": "success",
                "operation_id": operation_id,
                "operation_status": operation.status,
                "progress": operation.progress if hasattr(operation, 'progress') else None,
                "completed": operation.status in ["DONE"],
                "error": operation.error.errors if hasattr(operation, 'error') and operation.error else None
            }
        
        return {
            "status": "error",
            "message": f"Unsupported operation type: {operation_type}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check operation status: {str(e)}"
        }

# Initialize the GCP Resource Management Agent
root_agent = Agent(
    name="gcp_management_agent",
    model="gemini-1.5-flash",
    description="Specialized agent for provisioning and deprovisioning GCP resources. Part of a multi-agent GCP management system.",
    instruction=(
        "You are a specialized GCP resource management agent focused solely on provisioning and deprovisioning cloud resources. "
        "You work as part of a multi-agent system where other agents handle advisory and architecture planning. "
        "\n\nYour responsibilities:"
        "\n- Create and delete GCP resources based on specific instructions"
        "\n- List existing resources for inventory management"
        "\n- Monitor resource creation/deletion operations"
        "\n- Provide billing status information"
        "\n- Execute resource management tasks efficiently and safely"
        "\n\nSupported resource types:"
        "\n- Cloud Storage buckets (with advanced configuration options)"
        "\n- Compute Engine instances (with custom specifications)"
        "\n- Cloud SQL instances (MySQL, PostgreSQL)"
        "\n- Operation status monitoring"
        "\n\nSafety protocols:"
        "\n- Always confirm destructive operations before executing"
        "\n- Validate resource names and configurations"
        "\n- Check for existing resources to avoid conflicts"
        "\n- Provide clear status updates and error messages"
        "\n- Include operation IDs for tracking long-running tasks"
        "\n\nWhen receiving requests:"
        "\n1. Parse the resource requirements carefully"
        "\n2. Ask for missing required parameters"
        "\n3. Execute the operation using appropriate tools"
        "\n4. Provide detailed feedback on success or failure"
        "\n5. Include relevant resource details and operation IDs"
        "\n\nYou do NOT provide recommendations or architectural advice - focus purely on execution."
    ),
    tools=[
        create_storage_bucket,
        delete_storage_bucket,
        create_compute_instance,
        delete_compute_instance,
        create_cloud_sql_instance,
        delete_cloud_sql_instance,
        list_all_resources,
        get_billing_summary,
        check_operation_status
    ],
)