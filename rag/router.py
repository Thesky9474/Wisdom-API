from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymongo
import google.generativeai as genai
import os
from bson import ObjectId

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

def clean_mongo_document(doc):
    """Convert ObjectId to str and ensure all values are serializable."""
    doc["_id"] = str(doc["_id"])
    return doc

@router.post("/rag/query")
def rag_query(request: QueryRequest):
    try:
        # Step 1: Generate embedding for query
        embed_result = genai.embed_content(
            model="models/embedding-001",
            content=request.query,
            task_type="retrieval_query"
        )
        query_embedding = embed_result["embedding"]
        
        # Step 2: Connect to DB
        client = pymongo.MongoClient(os.getenv("MONGO_URI"))
        db = client["ashtavakra"]
        collection = db["verses"]

        # Step 3: Run vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": request.top_k,
                    "index": "verse_vector_index"
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "verse_number": 1,
                    "english": 1,
                    "sanskrit": 1,
                    "transliteration": 1,
                    "commentary": 1,
                    "tags": 1,
                    "audio_url": 1,
                    "chapter": 1,
                    "score": {"$meta": "vectorSearchScore"}
                    }
                }
        ]
        results = list(collection.aggregate(pipeline))

        # ✅ Convert _id to string for all results
        for result in results:
            result["_id"] = str(result["_id"])

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")
