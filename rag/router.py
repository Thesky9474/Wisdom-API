from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymongo, os, json
import google.generativeai as genai
from bson import ObjectId
from utils.cache import cache_get, cache_set

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
        cache_key = f"rag:{request.query}:{request.top_k}"

        # ✅ 1. Check cached results
        cached = cache_get(cache_key)
        if cached:
            return {"results": json.loads(cached)}
        
        # ✅ 2. Check cached embedding
        embed_key = f"embedding:{request.query}"
        cached_embed = cache_get(embed_key)
        if cached_embed:
            query_embedding = json.loads(cached_embed)
        else:
            embed_result = genai.embed_content(
                model="models/embedding-001",
                content=request.query,
                task_type="retrieval_query"
            )
            query_embedding = embed_result["embedding"]
            cache_set(embed_key, json.dumps(query_embedding), ttl=86400)
        
        # Step 3: Connect to DB
        client = pymongo.MongoClient(os.getenv("MONGO_URI"))
        db = client["ashtavakra"]
        collection = db["verses"]

        # Step 4: Run vector search
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

        for result in results:
            result["_id"] = str(result["_id"])

        # ✅ 5. Cache results (30 min TTL)
        cache_set(cache_key, json.dumps(results), ttl=1800)

        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")
