import os
import redis
from fastapi import HTTPException, Request

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

r = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True
)

def rate_limit(request: Request):
    ip = request.client.host
    key = f"rate_limit:{ip}"

    count = r.incr(key)

    if count == 1:
        r.expire(key, 60)

    if count > 5:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again in a minute.",
        )