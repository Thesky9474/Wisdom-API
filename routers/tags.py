from fastapi import APIRouter, HTTPException, Query, Depends
from db import db
from models import TagMap, Verse
from typing import List, Optional
import json
from utils.auth import optional_user
from utils.cache import cache_get, cache_set
from utils.serializers import serialize_list  

router = APIRouter()


# =========================================================
# GET ALL TAGS
# =========================================================
@router.get("/", response_model=List[TagMap])
async def get_tags(user=Depends(optional_user)):
    role = "auth" if user else "guest"
    cache_key = f"tags:{role}"

    # 🔹 Check Redis cache first
    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    # 🔹 Fetch tags from new structure
    cursor = db["tags"].find({}, {"_id": 0, "name": 1, "verses": 1})
    tag_items = await cursor.to_list(length=1000)

    if not tag_items:
        raise HTTPException(status_code=404, detail="Tags not found")

    # Guest: restrict to first 3 tags
    if role == "guest":
        tag_items = tag_items[:3]

    cache_set(cache_key, json.dumps(tag_items), ttl=86400)
    return tag_items


# =========================================================
# GET VERSES BY TAG
# =========================================================
@router.get("/tags/{tag}", response_model=List[Verse])
async def get_verses_by_tag(
    tag: str,
    user=Depends(optional_user),
    limit: Optional[int] = Query(None)
):
    role = "auth" if user else "guest"
    cache_key = f"tag:{role}:{tag}:{limit}"

    # 🔹 Check Redis cache
    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    # Guest restrictions
    guest_allowed_tags = ["Knowledge", "Liberation", "Renunciation"]
    if not user:
        if tag not in guest_allowed_tags:
            raise HTTPException(status_code=401, detail="Login required for this theme")
        if limit is None or limit > 3:
            limit = 3

    # 🔹 Fetch tag doc (new structure)
    tag_doc = await db["tags"].find_one({"name": tag})
    if not tag_doc:
        raise HTTPException(status_code=404, detail=f"No tag '{tag}' found")

    verse_numbers = tag_doc.get("verses", [])
    if not verse_numbers:
        raise HTTPException(status_code=404, detail=f"No verses found for tag '{tag}'")

    # 🔹 Fetch verses
    query = {"verse_number": {"$in": verse_numbers}}
    cursor = db["verses"].find(query)

    if limit:
        cursor = cursor.limit(limit)

    verses = await cursor.to_list(length=limit or 100)
    safe_verses = serialize_list(verses)

    cache_set(cache_key, json.dumps(safe_verses), ttl=86400)
    return safe_verses
