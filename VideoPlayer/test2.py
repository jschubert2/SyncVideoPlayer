#test connection to our redis server, taken from miro
import redis

# Connect to the Redis server
client = redis.Redis(
    host= '130.61.189.22', # Oracle Redis server address (AWS: 52.2.46.119)
    port=6379,            # Default Redis port
    db=0                  # Database number, 0 by default
)

# Test the connection
try:
    # Check if Redis server is running
    client.ping()
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Failed to connect to Redis.")

# set a value
client.set("my_example_key", "Example value")

# check if a key extists
exists = client.exists("my_example_key")
print("Key exists:" if exists else "Key does not exist")

# get a value
value = client.get("my_example_key")
print("GET:", "my_example_key:" + str(value))