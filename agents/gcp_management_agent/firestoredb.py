import os
from pprint import pprint
from typing import Dict

from google.cloud import firestore, firestore_admin_v1
from google.auth import default
from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud.firestore_admin_v1.types import Database


def create_firestore_database(database_id: str = "(default)", location_id: str = "nam5",
                              database_type: str = "FIRESTORE_NATIVE") -> Dict:
    credentials, project_id = default()

    if database_id == "(default)":
        db = firestore.Client(project=project_id, credentials=credentials)
        db.collection("init_check").document("ping").set({"status": "initialized"})
        return {
            "status": "success",
            "message": f"Default Firestore initialized in project {project_id}"
        }

    # Named database creation
    admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)
    parent = f"projects/{project_id}"
    db_path = f"{parent}/databases/{database_id}"

    try:
        admin_client.get_database(name=db_path)
        return {
            "status": "exists",
            "message": f"Named database '{database_id}' already exists."
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
        "message": f"Named database '{database_id}' created",
        "details": {
            "name": result.name,
            "location_id": result.location_id,
            "type": result.type_.name
        }
    }


import time
from google.api_core.exceptions import GoogleAPICallError

def delete_firestore_database(database_id: str = "(default)") -> Dict:
    credentials, project_id = default()

    if database_id == "(default)":
        db = firestore.Client(project=project_id, credentials=credentials)
        cleared = 0
        for col in db.collections():
            for doc in col.stream():
                doc.reference.delete()
                cleared += 1
        return {
            "status": "cleared",
            "message": f"Cleared {cleared} documents from default Firestore database"
        }

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
                raise TimeoutError(f"Timed out waiting for database '{database_id}' to be deleted.")
            time.sleep(10)

        op.result()  # ensure it's successful
        return {
            "status": "deleted",
            "message": f"Firestore database '{database_id}' deleted successfully"
        }

    except NotFound:
        return {
            "status": "error",
            "message": f"Named database '{database_id}' does not exist"
        }
    except GoogleAPICallError as e:
        return {
            "status": "error",
            "message": f"Database deletion failed: {str(e)}"
        }
    except TimeoutError as e:
        return {
            "status": "timeout",
            "message": str(e)
        }


def list_firestore_databases() -> Dict:
    credentials, project_id = default()
    admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)

    response = admin_client.list_databases(parent=f"projects/{project_id}")
    db_list = []

    for db in response.databases:
        db_list.append({
            "name": db.name,
            "type": getattr(db.type_, "name", "UNKNOWN"),
            "state": getattr(db.state, "name", "UNKNOWN") if hasattr(db, "state") else "UNKNOWN",
            "location_id": db.location_id,
            "create_time": str(db.create_time) if db.create_time else None,
        })

    return {
        "status": "success",
        "project_id": project_id,
        "databases": db_list
    }


# -----------------------------
# ✅ Test block
# -----------------------------
if __name__ == "__main__":
    print("📌 Creating default database...")
    pprint(create_firestore_database())

    print("\n📌 Creating named database 'testdb1'...")
    pprint(create_firestore_database("testdb1"))

    print("\n📌 Listing all databases...")
    pprint(list_firestore_databases())

    print("\n📌 Deleting named database 'testdb1'...")
    try:
        pprint(delete_firestore_database("testdb1"))
    except Exception as e:
        print(f"❌ Exception during deletion: {e}")

    print("\n📌 Clearing default database...")
    try:
        pprint(delete_firestore_database())
    except Exception as e:
        print(f"❌ Exception during clearing default database: {e}")
