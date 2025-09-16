import redis
import json, os
from bson import ObjectId

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # convert ObjectId → string
        return super().default(obj)

def cache_get(key):
    data = r.get(key)
    if data:
        return json.loads(data)
    return None

def cache_set(key, value, ttl=1800):
    # Use custom encoder
    r.set(key, json.dumps(value, cls=EnhancedJSONEncoder), ex=ttl)
