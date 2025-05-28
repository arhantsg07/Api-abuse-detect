from redis_client import get_redis_connection

def test_redis_connection():
    try:
        redis = get_redis_connection()
        if redis.ping():
            print("✅ Redis connection successful!")
            print(f"Redis host: {redis.connection_pool.connection_kwargs['host']}")
            print(f"Redis port: {redis.connection_pool.connection_kwargs['port']}")
        else:
            print("❌ Redis connection failed!")
    except Exception as e:
        print(f"❌ Redis connection error: {str(e)}")

if __name__ == "__main__":
    test_redis_connection() 