#set scheduler manually to reset
import redis
import json

# Connect to Redis
redis_client = redis.StrictRedis(host='130.61.189.22', port=6379, decode_responses=False)

# Data to set in Redis (scheduler data)
scheduler_data = {
    "song_name": "fixyou",
    "t": "1600000000",  # This is a placeholder timestamp (adjust as needed)
    "d": "18",       # Duration in seconds
    "c": "0",           # Current position in the song (for example, where the song was stopped)
    "st": "Pause"        # "Play" or "Stop" state
}

# Set the Redis key "3:sc" with the scheduler data
redis_client.set("3:sc", json.dumps(scheduler_data))

print("Scheduler data set in Redis.")
