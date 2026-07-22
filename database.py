import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/food-genie")
DB_NAME = os.getenv("DB_NAME", "food-genie")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

def serialize_doc(doc):
    """
    Helper function to convert MongoDB document _id (ObjectId)
    and nested ObjectIds into string representations for JSON/Pydantic serialization.
    """
    if doc is None:
        return None
    
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if k == "_id":
                new_doc["id"] = str(v)
            elif isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif isinstance(v, (dict, list)):
                new_doc[k] = serialize_doc(v)
            else:
                new_doc[k] = v
        return new_doc
    
    if isinstance(doc, ObjectId):
        return str(doc)
    
    return doc

def parse_object_id(id_str: str) -> ObjectId:
    """Safely converts string to BSON ObjectId."""
    try:
        return ObjectId(id_str)
    except Exception:
        return None
