from bson import ObjectId

def serialize_doc(doc):
    """Convert MongoDB document to JSON-safe dict"""
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])  # ObjectId → string
    return doc

def serialize_list(docs):
    """Convert list of MongoDB documents"""
    return [serialize_doc(doc) for doc in docs]
