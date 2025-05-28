# detector.py
import redis
import json
import redis_client
import pickle
import numpy as np

BLOCKED_KEY = "anomaly:blocked_clients"
ANOMALY_LOG_KEY = "anomaly:logs"

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

def extract_features(log):
    return [
        log.get("request_count", 0),
        log.get("avg_request_interval", 1.0),
        log.get("unique_endpoints", 1),
    ]

def is_anomalous(log):
    features = np.array(extract_features(log)).reshape(1, -1)
    prediction = model.predict(features)
    return prediction[0] == -1  # -1 means anoma

def run_anomaly_detection():
    logs = redis_client.lrange("usage_logs", 0, -1)
    parsed = [json.loads(log.decode()) for log in logs]

    # Perform detection...
    blocked = []

    for log in parsed:
        if is_anomalous(log):  # Assume this is your isolation forest check
            client_id = log["client_id"]
            blocked.append(client_id)
            redis_client.sadd(BLOCKED_KEY, client_id)

    return blocked

def get_detection_stats():
    blocked = list(redis_client.smembers(BLOCKED_KEY))
    blocked = [b.decode() for b in blocked]

    count = len(blocked)
    return {
        "blocked_clients": blocked,
        "blocked_count": count,
        "detection_algorithm": "Isolation Forest",
    }
