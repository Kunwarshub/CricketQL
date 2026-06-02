import redis
import os

_redis = None

def get_redis():
    global _redis

    if _redis == None:
        try:
            REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
            _redis = redis.from_url(REDIS_URL, decode_responses=True, ssl_cert_reqs=None)
            _redis.ping()
        except Exception as e:
            print(f"Redis connection error: {e}")
            _redis = None

    return _redis


def get_cache(key):

    r = get_redis()
    if r is None:
        return None

    try:
        return r.get(key)
    except redis.ConnectionError:
        return None


def set_cache(key, value, ttl=3600):
    r = get_redis()
    if r is None:
        print("Redis not available")
        return
    try:
        if ttl:
            result = r.set(key, value, ex=ttl)
            print(f"set_cache result: {result}, key: {key}")
        else:
            result = r.set(key, value)
            print(f"set_cache result: {result}, key: {key}")
    except Exception as e:  
        print(f"set_cache error: {e}")