import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    r.ping()
    redis_available = True
except Exception as e:
    r = None
    redis_available = False


def get_cache(key):

    if not redis_available:
        return None

    try:
        value = r.get(key)
        if value is not None:
            return value
    except redis.ConnectionError:
        return None

    return None


def set_cache(key, sql):

    if not redis_available:
        return

    try:
        r.set(key, sql, ex=3600)  # TTL
    except redis.ConnectionError:
        pass