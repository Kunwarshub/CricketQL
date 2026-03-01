import redis

try:
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.ping()
    redis_available = True
except redis.ConnectionError:
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