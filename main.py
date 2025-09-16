from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
import logging
import os
from db import db
from utils.cache import cache_set, r
from routers.verses import router as verse_router
from routers import tags
from models import LoginRequest
from rag.router import router as rag_router
from utils.auth import create_access_token, get_current_user

# =========================================
# LOGGING CONFIG
# =========================================
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("wisdom-api")

app = FastAPI()

# =========================================
# CORS SETTINGS (Strict)
# =========================================
allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
origins = allowed_origins_str.split(" ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],   # restrict
    allow_headers=["Authorization", "Content-Type"],  # restrict
)

# =========================================
# SECURITY HEADERS MIDDLEWARE
# =========================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# =========================================
# STARTUP CACHE WARMING
# =========================================
@app.on_event("startup")
async def warm_cache():
    logger.info("🚀 Warming Redis cache with guest data...")

    # Preload guest chapter 1 (first 5 verses)
    chapter_1 = await db["verses"].find({"chapter": 1}).limit(5).to_list(length=5)
    cache_set("chapter:guest:1:5", chapter_1, ttl=1800)

    # Preload guest tags
    guest_tags = ["Knowledge", "Liberation", "Renunciation"]
    tag_doc = await db["tags"].find_one() or {}

    for tag in guest_tags:
        verse_numbers = tag_doc.get(tag, [])
        verses = await db["verses"].find({"verse_number": {"$in": verse_numbers}}).limit(3).to_list(length=3)
        cache_set(f"tag:guest:{tag}:3", verses, ttl=86400)

    logger.info("✅ Guest cache warmed")

# =========================================
# GZIP COMPRESSION
# =========================================
app.add_middleware(GZipMiddleware, minimum_size=500)

# =========================================
# AUTH ROUTES
# =========================================
@app.post("/login")
def login(req: LoginRequest):
    token = create_access_token({"sub": req.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
def protected(user=Depends(get_current_user)):
    if not user:
        return {"message": "Guest user → limited access"}
    return {"message": f"Hello {user['username']}, full access granted"}

# =========================================
# HEALTH ENDPOINTS
# =========================================
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
async def readiness():
    try:
        # Check MongoDB
        await db.command("ping")
        # Check Redis
        r.ping()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "unavailable"})

# =========================================
# ROUTERS
# =========================================
app.include_router(verse_router, prefix="/verses")
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(rag_router, prefix="/rag", tags=["rag"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Wisdom of Ashtavakra API"}
