# rate_limiter/train_model.py
import json
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from redis_client import get_redis_connection
import time
from collections import defaultdict

REDIS_HISTORY_KEY = "usage_history"
MODEL_FILE = "model.pkl"
MODEL_STATS_KEY = "model:training:stats"

def extract_features_from_history(history_data):
    # Group historical data by client_id
    client_activity = defaultdict(list)
    for event in history_data:
        client_id = event["client_id"]
        client_activity[client_id].append(event["timestamp"])

    features_list = []
    # Analyze each client's activity
    for client_id, timestamps in client_activity.items():
        timestamps.sort() # Ensure timestamps are sorted
        request_count = len(timestamps)
        
        # Calculate average interval
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals) if intervals else 1.0

        # Calculate requests per minute
        # We need a time window for this, for simplicity let's just use total requests and avg interval for now as in detector.py
        requests_per_minute = 60 / avg_interval if avg_interval > 0 else 0

        # This should match the features used in detector.py's extract_features
        features_list.append([
            requests_per_minute,
            request_count
        ])

    return np.array(features_list)

def train_dynamic_model():
    redis_conn = get_redis_connection()
    
    # Fetch usage history from Redis
    raw_history = redis_conn.lrange(REDIS_HISTORY_KEY, 0, -1)
    history_data = [json.loads(item) for item in raw_history]
    
    if not history_data:
        print("No usage history data found in Redis. Cannot train model.")
        # Optionally, train with dummy data or load existing model if available
        # For now, we exit if no data
        return False
        
    print(f"Fetched {len(history_data)} usage history records.")

    # Extract features from history data
    X = extract_features_from_history(history_data)
    
    if X.shape[0] == 0:
         print("No valid features extracted from history data. Cannot train model.")
         return False
         
    print(f"Extracted features with shape: {X.shape}")

    # Train Isolation Forest
    # Adjust contamination based on expected anomaly rate in your data
    model = IsolationForest(contamination='auto', random_state=42)
    model.fit(X)

    # Save the trained model
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)

    # Save training stats to Redis
    training_stats = {
        "last_trained_timestamp": int(time.time()),
        "training_data_count": len(history_data)
    }
    redis_conn.hmset(MODEL_STATS_KEY, training_stats) # Use hmset for older redis-py versions
    # For newer redis-py, use: redis_conn.hset(MODEL_STATS_KEY, mapping=training_stats)

    print("✅ Dynamic model trained and saved to model.pkl")
    print(f"✅ Training stats saved to Redis key: {MODEL_STATS_KEY}")
    return True

if __name__ == "__main__":
    train_dynamic_model()
