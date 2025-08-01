from fastapi import APIRouter, HTTPException
from db import db
from models import Verse
from typing import List, Optional
from bson import ObjectId

router = APIRouter()

# Utility: Clean MongoDB doc
def clean_verse(verse):
    if "_id" in verse:
        verse["_id"] = str(verse["_id"])
    return verse

# --- Specific routes should come BEFORE dynamic routes ---

@router.get("/random", response_model=Verse)
async def get_random_verse():
    """
    Selects and returns a single random verse from the database using
    an efficient aggregation pipeline.
    """
    pipeline = [{"$sample": {"size": 1}}]
    random_verse_cursor = db["verses"].aggregate(pipeline)
    random_verse_list = await random_verse_cursor.to_list(length=1)
    
    if not random_verse_list:
        raise HTTPException(status_code=404, detail="No verses found in database to select from.")
        
    return clean_verse(random_verse_list[0])

@router.get("/chapters", response_model=List[int])
async def get_all_chapters():
    """
    Retrieves a sorted list of unique chapter numbers.
    """
    chapters_list = await db["verses"].distinct("chapter")
    chapters_list.sort()
    return chapters_list

@router.get("/chapter/{chapter}", response_model=List[Verse])
async def get_verses_by_chapter(chapter: int, limit: Optional[int] = None):
    """Retrieves verses for a chapter, with an optional limit."""
    cursor = db["verses"].find({"chapter": chapter})
    if limit:
        cursor = cursor.limit(limit)
    verses = await cursor.to_list(length=limit or 200)
    return [clean_verse(v) for v in verses]

@router.get("/verse_number/{verse_number}", response_model=Verse)
async def get_by_verse_number(verse_number: str):
    verse = await db["verses"].find_one({"verse_number": verse_number})
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    return clean_verse(verse)

# --- Dynamic/Generic routes should come LAST ---

@router.get("/{verse_id}", response_model=Verse)
async def get_single_verse(verse_id: str):
    """
    This route now comes after specific string routes like /random
    to avoid incorrect matching.
    """
    try:
        obj_id = ObjectId(verse_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid verse ID")

    verse = await db["verses"].find_one({"_id": obj_id})
    if verse is None:
        raise HTTPException(status_code=404, detail="Verse not found")

    return clean_verse(verse)

# The "/" route can be here or at the end as it doesn't conflict.
@router.get("/", response_model=List[Verse])
async def get_all_verses():
    cursor = db["verses"].find()
    verses = await cursor.to_list(length=1000)
    return [clean_verse(v) for v in verses]