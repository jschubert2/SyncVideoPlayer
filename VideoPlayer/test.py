#test wether the key has a value in redis
import redis

# Connect to Redis
redis_client = redis.StrictRedis(host='130.61.189.22', port=6379, decode_responses=True)

# Fetch and print the value
key = "3:sc"
value = redis_client.get(key)

if value:
    print(f"Value of {key}: {value}")
else:
    print(f"{key} does not exist.")
