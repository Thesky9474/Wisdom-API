from fastapi import APIRouter, HTTPException, Depends
from db import db
from models import Verse
from typing import List, Optional
import json
from utils.serializers import serialize_list, serialize_doc
from utils.cache import cache_get, cache_set
from utils.auth import optional_user   

router = APIRouter()

@router.get("/random", response_model=Verse)
async def get_random_verse():
    pipeline = [{"$sample": {"size": 1}}]
    random_verse_cursor = db["verses"].aggregate(pipeline)
    random_verse_list = await random_verse_cursor.to_list(length=1)

    if not random_verse_list:
        raise HTTPException(status_code=404, detail="No verses found")

    return serialize_doc(random_verse_list[0])


@router.get("/chapters", response_model=List[int])
async def get_all_chapters(user=Depends(optional_user)):
    role = "auth" if user else "guest"
    cache_key = f"chapters:{role}"

    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    chapters_list = await db["verses"].distinct("chapter")
    chapters_list.sort()

    if role == "guest":
        chapters_list = [1]   # only Chapter 1 for guests

    cache_set(cache_key, json.dumps(chapters_list), ttl=43200)
    return chapters_list


@router.get("/chapter/{chapter}", response_model=List[Verse])
async def get_verses_by_chapter(chapter: int, skip: int = 0, limit: Optional[int] = 50, user=Depends(optional_user)):
    role = "auth" if user else "guest"
    cache_key = f"chapter:{role}:{chapter}:{skip}:{limit}"

    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    if not user:
        if chapter != 1:
            raise HTTPException(status_code=401, detail="Login required to view other chapters")
        if limit is None or limit > 5:
            limit = 5
            
    cursor = db["verses"].find({"chapter": chapter}).skip(skip).limit(limit)
    verses = await cursor.to_list(length=limit or 50)


    verses = serialize_list(verses)
    cache_set(cache_key, json.dumps(verses), ttl=43200)
    return verses


@router.get("/verse_number/{verse_number}", response_model=Verse)
async def get_by_verse_number(verse_number: str, user=Depends(optional_user)):
    role = "auth" if user else "guest"
    cache_key = f"verse_number:{role}:{verse_number}"

    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    verse = await db["verses"].find_one({"verse_number": verse_number})
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")

    if role == "guest" and verse.get("chapter") != 1:
        return {"message": "Not available for guest users"}

    verse = serialize_doc(verse)
    cache_set(cache_key, json.dumps(verse), ttl=43200)
    return verse


@router.get("/", response_model=List[Verse])
async def get_all_verses(skip: int = 0, limit: int = 50, user=Depends(optional_user)):
    role = "auth" if user else "guest"
    cache_key = f"all_verses:{role}:{skip}:{limit}"

    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)

    cursor = db["verses"].find().skip(skip).limit(limit)
    verses = await cursor.to_list(length=limit or 50)

    if role == "guest":
        verses = [v for v in verses if v.get("chapter") == 1][:5]

    verses = serialize_list(verses)
    cache_set(cache_key, json.dumps(verses), ttl=43200)
    return verses
