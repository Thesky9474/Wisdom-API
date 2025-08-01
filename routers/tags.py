from fastapi import APIRouter, HTTPException, Query
from db import db
from models import TagMap
from models import Verse
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[TagMap])
async def get_all_tags():
    try:
        tag_doc = await db["tags"].find_one()
        if not tag_doc:
            raise HTTPException(status_code=404, detail="Tags not found")

        # Convert to list of TagMap objects
        tag_list = [
            {"name": tag, "verses": verses}
            for tag, verses in tag_doc.items()
            if tag != "_id"
        ]
        return tag_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags/{tag}", response_model=List[Verse])
async def get_verses_by_tag(tag: str, limit: Optional[int] = Query(None)): # ✨ ADD limit parameter
    tag_doc = await db["tags"].find_one() # Use await for async driver
    verse_numbers = tag_doc.get(tag, [])

    if not verse_numbers:
        raise HTTPException(status_code=404, detail=f"No verses found for tag '{tag}'")

    # Build the query
    query = {"verse_number": {"$in": verse_numbers}}
    cursor = db["verses"].find(query)

    # Apply the limit if it's provided
    if limit:
        cursor = cursor.limit(limit)

    verses = await cursor.to_list(length=limit or 100) # Use await
    return verses

