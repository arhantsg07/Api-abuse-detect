import json
import time
from redis_client import get_redis_connection

redis = get_redis_connection()
HISTORY_KEY = "usage_history"

def log_usage_data(client_id):
    event = {
        "timestamp": int(time.time()),
        "client_id": client_id
    }
    redis.rpush(HISTORY_KEY, json.dumps(event))
    redis.ltrim(HISTORY_KEY, -10000, -1)  # keep last 10k records

def fetch_usage_data():
    raw_data = redis.lrange(HISTORY_KEY, 0, -1)
    return [json.loads(x) for x in raw_data]
