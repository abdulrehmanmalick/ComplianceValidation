from db_connection import get_database
from bson.objectid import ObjectId
from datetime import datetime

def add_document(pointer_id, document_name, document_data):
    """
    Adds a document linked to a specific pointer in the database.
    """
    db = get_database()
    documents_collection = db["documents"]
    document_entry = {
        "pointer_id": ObjectId(pointer_id),
        "document_name": document_name,
        "document_data": document_data,
        "upload_date": datetime.now()
    }
    result = documents_collection.insert_one(document_entry)
    return str(result.inserted_id)

def get_documents_by_pointer(pointer_id):
    """
    Retrieves all documents linked to a specific pointer from the database.
    """
    db = get_database()
    documents_collection = db["documents"]
    documents = list(documents_collection.find({"pointer_id": ObjectId(pointer_id)}))
    return documents

def update_document(document_id, updates):
    """
    Updates a specific document in the database.
    """
    db = get_database()
    documents_collection = db["documents"]
    result = documents_collection.update_one(
        {"_id": ObjectId(document_id)}, {"$set": updates}
    )
    return result.modified_count

def delete_document(document_id):
    """
    Deletes a specific document from the database.
    """
    db = get_database()
    documents_collection = db["documents"]
    result = documents_collection.delete_one({"_id": ObjectId(document_id)})
    return result.deleted_count

def delete_documents_by_pointer(pointer_id):
    db = get_database()
    documents_collection = db["documents"]  
    result = documents_collection.delete_many({"pointer_id": ObjectId(pointer_id)})
    return result.deleted_count
