from pydantic import BaseModel
from typing import List, Optional

class Verse(BaseModel):
    chapter: int
    chapter_title: str
    verse_number: str
    sanskrit: str
    transliteration: str
    english: str
    commentary: str
    tags: List[str]
    audio_url: Optional[str] = None
    _id: Optional[str] = None  # Include if you convert ObjectId to string

    class Config:
        orm_mode = True

class Tag(BaseModel):
    name: str
    verses: List[str]

class TagMap(BaseModel):
    name: str
    verses: List[str]