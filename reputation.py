from redis_client import get_redis_connection

redis_conn = get_redis_connection()
BLOCK_THRESHOLD = -5

def update_reputation(client_id, delta):
    # score_key = f"reputation:{client_id}"
    # redis_conn.incrby(score_key, delta)
    # redis_conn.expire(score_key, 3600)
    key = f"reputation:{client_id}"
    new_score = redis_conn.incrby(key, delta)

    # If the score drops below threshold, block the client
    if new_score <= BLOCK_THRESHOLD:
        redis_conn.set(f"blocked:{client_id}", 1)

def get_reputation(client_id):
    return int(redis_conn.get(f"reputation:{client_id}") or 0)

def is_blocked(client_id):
    return redis_conn.exists(f"blocked:{client_id}")