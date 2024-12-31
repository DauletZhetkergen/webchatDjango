import redis

r = redis.Redis(host='172.27.194.24', port=6379, db=0)

try:
    r.ping()
    print("Connected to Redis")
except redis.ConnectionError:
    print("Failed to connect to Redis")