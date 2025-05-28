import requests
from flask import Flask, request, jsonify
from limiter import is_rate_limited
from reputation import update_reputation, get_reputation, is_blocked
from config import ENVOY_ADMIN_URL
from anomaly import log_usage_data
from detector import get_detection_stats

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def api():
    client_ip = request.remote_addr
    api_key = request.headers.get("x-api-key", "anonymous")
    
    ip_limited = is_rate_limited(f"ip:{client_ip}")
    key_limited = is_rate_limited(f"key:{api_key}")
    
    client_id = f"{client_ip}:{api_key}"

    log_usage_data(client_id)


    if is_blocked(client_id):
        return jsonify({"error": "Client is blocked due to abnormal activity"}), 403

    if ip_limited or key_limited:
        update_reputation(client_id, -1)
        return jsonify({"error": "Rate limit exceeded", "reputation": get_reputation(client_id)}), 429

    # if is_rate_limited(client_id):
    #     update_reputation(client_id, -1)
    #     return jsonify({"error": "Rate limit exceeded", "reputation": get_reputation(client_id)}), 429

    update_reputation(client_id, 1)
    return jsonify({"message": "Request successful", "reputation": get_reputation(client_id)})

@app.route("/metrics", methods=["GET"])
def metrics():
    try:
        response = requests.get(f"{ENVOY_ADMIN_URL}/stats/prometheus")
        return response.text, 200, {'Content-Type': 'text/plain'}
    except requests.RequestException:
        return jsonify({"error": "Failed to fetch Envoy metrics"}), 500




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5002)
