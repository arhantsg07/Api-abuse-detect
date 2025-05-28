# detector.py
import redis
import json
import redis_client
import pickle
import numpy as np
import time

BLOCKED_KEY = "anomaly:blocked_clients"
ANOMALY_LOG_KEY = "anomaly:logs"
HISTORY_KEY = "usage_history"

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

def extract_features(log):
    # Calculate requests per minute
    request_count = log.get("request_count", 0)
    avg_interval = log.get("avg_request_interval", 1.0)
    requests_per_minute = 60 / avg_interval if avg_interval > 0 else 0
    
    return [
        requests_per_minute,  # requests_per_minute
        request_count        # total_requests
    ]

def is_anomalous(log):
    features = np.array(extract_features(log)).reshape(1, -1)
    prediction = model.predict(features)
    score = model.score_samples(features)
    print(f"Features: {features}, Prediction: {prediction}, Score: {score}")
    return prediction[0] == -1  # -1 means anomaly

def run_anomaly_detection():
    redis_conn = redis_client.get_redis_connection()
    logs = redis_conn.lrange(HISTORY_KEY, 0, -1)
    parsed = [json.loads(log) for log in logs]
    print(f"Processing {len(parsed)} logs")

    # Group logs by client_id
    client_logs = {}
    for log in parsed:
        client_id = log["client_id"]
        if client_id not in client_logs:
            client_logs[client_id] = []
        client_logs[client_id].append(log)

    # Analyze each client's behavior
    blocked = []
    for client_id, logs in client_logs.items():
        print(f"\nAnalyzing client: {client_id}")
        # Calculate features
        request_count = len(logs)
        timestamps = [log["timestamp"] for log in logs]
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals) if intervals else 1.0

        client_data = {
            "request_count": request_count,
            "avg_request_interval": avg_interval
        }
        print(f"Client data: {client_data}")

        if is_anomalous(client_data):
            print(f"Anomaly detected for client: {client_id}")
            blocked.append(client_id)
            redis_conn.sadd(BLOCKED_KEY, client_id)

    return blocked

def get_detection_stats():
    try:
        redis_conn = redis_client.get_redis_connection()
        print("Redis connection established")
        
        # Run anomaly detection
        run_anomaly_detection()
        
        # Get blocked clients
        blocked = list(redis_conn.smembers(BLOCKED_KEY))
        print(f"Blocked clients from Redis: {blocked}")
        
        count = len(blocked)
        return {
            "blocked_clients": blocked,
            "blocked_count": count,
            "detection_algorithm": "Isolation Forest",
            "redis_status": "connected"
        }
    except Exception as e:
        print(f"Redis error: {str(e)}")
        return {
            "error": str(e),
            "blocked_clients": [],
            "blocked_count": 0,
            "detection_algorithm": "Isolation Forest",
            "redis_status": "error"
        }
