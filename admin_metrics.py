# from flask import Flask, jsonify
# from flask_cors import CORS
# import redis

# app = Flask(__name__)
# CORS(app)
# r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

# @app.route('/admin/metrics')
# def get_metrics():
#     ip_keys = r.keys('rate_limit:ip:*')
#     key_keys = r.keys('rate_limit:key:*')
#     rep_keys = r.keys('reputation:*')
#     blocked_keys = r.keys('blocked:*')

#     def make_dict(keys):
#         return {k: r.get(k) for k in keys}

#     return jsonify({
#         "rate_by_ip": make_dict(ip_keys),
#         "rate_by_key": make_dict(key_keys),
#         "reputation_scores": make_dict(rep_keys),
#         "blocked_requests": make_dict(blocked_keys)
#     })

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=8082)
from flask import Flask, jsonify
from flask_cors import CORS
import redis
import re
from collections import defaultdict

from rate_limiter.detector import get_detection_stats

app = Flask(__name__)
CORS(app)
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

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

    return jsonify({
        "rate_by_ip": ip_data,
        "rate_by_key": key_data,
        "reputation_scores": reputation,
        "blocked_requests": blocked
    })

@app.route("/admin/detection-stats", methods=["GET"])
def detection_stats():
    stats = get_detection_stats()
    return jsonify(stats)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082)
