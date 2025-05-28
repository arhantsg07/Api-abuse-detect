REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0

ENVOY_ADMIN_URL = 'http://localhost:9901'
RATE_LIMITS = {
    'default': {'limit': 15, 'window_seconds': 60},
    'sliding_window': {'interval': 10, 'segments': 6}  # 10s * 6 = 60s window
}
