from db_connection import get_database
from bson.objectid import ObjectId
from datetime import datetime

def add_compliance_result(pointer_id, compliance_status, details):
    """
    Adds a compliance result linked to a specific pointer in the database.
    """
    db = get_database()
    compliance_collection = db["compliance_results"]
    compliance_entry = {
        "pointer_id": ObjectId(pointer_id),
        "compliance_status": compliance_status,
        "details": details,
        "checked_date": datetime.now()
    }
    result = compliance_collection.insert_one(compliance_entry)
    return str(result.inserted_id)

def get_compliance_results_by_pointer(pointer_id):
    """
    Retrieves all compliance results linked to a specific pointer from the database.
    """
    db = get_database()
    compliance_collection = db["compliance_results"]
    results = list(compliance_collection.find({"pointer_id": ObjectId(pointer_id)}))
    return results

def update_compliance_result(result_id, updates):
    """
    Updates a specific compliance result in the database.
    """
    db = get_database()
    compliance_collection = db["compliance_results"]
    result = compliance_collection.update_one(
        {"_id": ObjectId(result_id)}, {"$set": updates}
    )
    return result.modified_count

def delete_compliance_result(result_id):
    """
    Deletes a specific compliance result from the database.
    """
    db = get_database()
    compliance_collection = db["compliance_results"]
    result = compliance_collection.delete_one({"_id": ObjectId(result_id)})
    return result.deleted_count
