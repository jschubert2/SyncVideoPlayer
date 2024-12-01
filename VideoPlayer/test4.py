#upload video as binary to test
import redis


# Function to convert video to binary and upload to Redis
def upload_video_to_redis(video_file_path, song_name):
    try:
        # Open the video file in binary mode
        with open(video_file_path, 'rb') as video_file:
            video_binary = video_file.read()

        # Connect to Redis
        redis_client = redis.StrictRedis(host='130.61.189.22', port=6379, decode_responses=False)

        # Redis key to store the video (1:Song_Name:vi)
        redis_key = f"1:{song_name}:vi"

        # Upload the video as binary to Redis
        redis_client.set(redis_key, video_binary)

        print(f"Video {song_name} uploaded to Redis with key: {redis_key}")

    except Exception as e:
        print(f"Error: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Path to the video file (e.g., static/fixyou.mp4)
    video_file_path = 'static/fixyou.mp4'  # Update the path as needed
    song_name = 'fixyou'  # Example song name

    # Upload video to Redis
    upload_video_to_redis(video_file_path, song_name)
