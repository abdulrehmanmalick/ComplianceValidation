from db_connection import get_database
from bson.objectid import ObjectId

def add_pointer(pointer_data):
    db = get_database()
    pointers_collection = db["pointers"]
    result = pointers_collection.insert_one(pointer_data)
    return str(result.inserted_id)

def get_all_pointers():
    db = get_database()
    pointers_collection = db["pointers"]
    return list(pointers_collection.find())

def update_pointer(pointer_id, updates):
    db = get_database()
    pointers_collection = db["pointers"]
    result = pointers_collection.update_one(
        {"_id": ObjectId(pointer_id)}, {"$set": updates}
    )
    return result.modified_count

def delete_pointer(pointer_id):
    db = get_database()
    pointers_collection = db["pointers"]
    result = pointers_collection.delete_one({"_id": ObjectId(pointer_id)})
    return result.deleted_count
