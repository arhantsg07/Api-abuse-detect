from flask import Flask, jsonify
from flask_cors import CORS
import redis
import re
from collections import defaultdict

from detector import get_detection_stats
from redis_client import get_redis_connection

app = Flask(__name__)
CORS(app)
r = get_redis_connection()

def aggregate_by_entity(keys, prefix):
    data = defaultdict(int)
    pattern = re.compile(f"{prefix}:(.*?):\\d+$")  # Extract IP/key and segment number
    for key in keys:
        match = pattern.match(key)
        if match:
            entity = match.group(1)
            count = r.get(key)
            data[entity] += int(count) if count else 0
    return data

@app.route('/admin/metrics')
def get_metrics():
    ip_data = aggregate_by_entity(r.keys('rate_limit:ip:*'), 'rate_limit:ip')
    key_data = aggregate_by_entity(r.keys('rate_limit:key:*'), 'rate_limit:key')

    reputation = {k: r.get(k) for k in r.keys('reputation:*')}
    blocked = {k: r.get(k) for k in r.keys('blocked:*')}
    
    # Fetch model training stats
    model_stats_key = "model:training:stats"
    model_stats = r.hgetall(model_stats_key)
    print(f"[DEBUG] Fetched model_stats from Redis: {model_stats}") # Debug print

    return jsonify({
        "rate_by_ip": ip_data,
        "rate_by_key": key_data,
        "reputation_scores": reputation,
        "blocked_requests": blocked,
        "model_training_stats": model_stats
    })

@app.route("/admin/detection-stats", methods=["GET"])
def detection_stats():
    stats = get_detection_stats()
    return jsonify(stats)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082)
