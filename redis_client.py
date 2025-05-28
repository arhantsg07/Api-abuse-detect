import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

_redis_connection = None

def get_redis_connection():
    global _redis_connection
    if _redis_connection is None:
        _redis_connection = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    return _redis_connection

def smembers(key):
    return get_redis_connection().smembers(key)

def sadd(key, value):
    return get_redis_connection().sadd(key, value)

def lrange(key, start, end):
    return get_redis_connection().lrange(key, start, end)
