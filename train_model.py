# rate_limiter/train_model.py
import json
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

# Step 1: Generate dummy usage data
dummy_data = [
    {"requests_per_minute": 5, "total_requests": 100},
    {"requests_per_minute": 4, "total_requests": 110},
    {"requests_per_minute": 3, "total_requests": 90},
    {"requests_per_minute": 7, "total_requests": 105},
    {"requests_per_minute": 100, "total_requests": 10000},  # Anomalous
    {"requests_per_minute": 120, "total_requests": 15000},  # Anomalous
]

# Step 2: Convert to numpy array
X = np.array([[d["requests_per_minute"], d["total_requests"]] for d in dummy_data])

# Step 3: Train Isolation Forest
model = IsolationForest(contamination=0.2, random_state=42)
model.fit(X)

# Step 4: Save the trained model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved to model.pkl")
