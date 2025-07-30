from fastapi import APIRouter, HTTPException
from db import db
from models import TagMap
from models import Verse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[TagMap])
async def get_all_tags():
    try:
        tag_doc = db["tags"].find_one()
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
async def get_verses_by_tag(tag: str):
    tag_doc = db["tags"].find_one()
    verse_numbers = tag_doc.get(tag, [])

    if not verse_numbers:
        raise HTTPException(status_code=404, detail=f"No verses found for tag '{tag}'")

    verses = db["verses"].find({"verse_number": {"$in": verse_numbers}}).to_list(length=100)
    return verses

