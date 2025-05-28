import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

def get_redis_connection():
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
