import redis

try:
    client = redis.StrictRedis(host='localhost', port=6379, db=0)
    response = client.ping()
    if response:
        print("Redis is reachable")
except redis.ConnectionError:
    print("Redis is not reachable")