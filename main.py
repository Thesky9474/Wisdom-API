from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.verses import router as verse_router
from routers import tags
from rag.router import router as rag_router

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:5000",
    "https://your-frontend-app.vercel.app",
    "https://your-backend-server.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(verse_router, prefix="/verses")
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Wisdom of Ashtavakra API"}
