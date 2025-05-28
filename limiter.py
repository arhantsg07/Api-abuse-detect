import time
from redis_client import get_redis_connection
from config import RATE_LIMITS
from flask import Request

redis_conn = get_redis_connection()

def get_bucket_key(client_id, segment):
    # return f"rate:{client_id}:bucket:{segment}"
    if client_id.startswith("ip:"):
        return f"rate_limit:{client_id}:{segment}"
    elif client_id.startswith("key:"):
        return f"rate_limit:{client_id}:{segment}"
    else:
        return f"rate_limit:other:{client_id}:{segment}"

def is_rate_limited(client_id):
    now = int(time.time())
    config = RATE_LIMITS['sliding_window']
    interval = config['interval']
    segments = config['segments']
    current_segment = now // interval

    keys = [get_bucket_key(client_id, current_segment - i) for i in range(segments)]
    pipeline = redis_conn.pipeline()
    for key in keys:
        pipeline.get(key)
    counts = pipeline.execute()

    total_requests = sum(int(c) if c else 0 for c in counts)
    if total_requests >= RATE_LIMITS['default']['limit']:
        return True

    # Increment current segment bucket
    current_key = get_bucket_key(client_id, current_segment)
    redis_conn.incr(current_key)
    redis_conn.expire(current_key, interval * segments)

    return False

def apply_rate_limit(request: Request):
    ip = request.remote_addr
    api_key = request.headers.get('X-API-Key')

    ip_limited = is_rate_limited(f"ip:{ip}")
    key_limited = is_rate_limited(f"key:{api_key}") if api_key else False

    return ip_limited or key_limited