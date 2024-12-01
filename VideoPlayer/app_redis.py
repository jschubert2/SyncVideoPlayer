from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import redis
import time
import json
from datetime import datetime
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, message_queue='redis://130.61.189.22:6379')

# Connect to Redis
redis_client = redis.StrictRedis(host='130.61.189.22', port=6379, decode_responses=False)

# Function to retrieve video binary data
def get_video_data(song_name):
    key = f"1:{song_name}:vi"
    video_binary = redis_client.get(key)
    if not video_binary:
        raise FileNotFoundError(f"Video data for {song_name} not found in Redis.")
    return video_binary

# Route to serve the video dynamically
@app.route("/video/<song_name>")
def serve_video(song_name):
    try:
        video_binary = get_video_data(song_name)
        # Return video as a response
        return Response(video_binary, mimetype="video/mp4")
    except FileNotFoundError as e:
        return str(e), 404

# Sync request handler
@socketio.on("sync_request")
def handle_sync_request():
    try:
        # Fetch scheduler data from Redis
        scheduler_data = redis_client.get("3:sc")
        if scheduler_data:
            scheduler_data = json.loads(scheduler_data)
            emit("sync_state", scheduler_data)
        else:
            emit("sync_state", {"error": "No scheduler data found in Redis."})
    except Exception as e:
        emit("sync_state", {"error": str(e)})

# Function to handle play/pause request and update the scheduler in Redis
@socketio.on("play_pause")
def handle_play_pause(data):
    print("playing/pausing")
    try:
        # Fetch the current scheduler data from Redis
        scheduler_data = redis_client.get("3:sc")
        if scheduler_data:
            scheduler_data = json.loads(scheduler_data)

            # Extract details from incoming data
            client_song_name = data.get("song_name")
            client_current_time = data.get("current_time")
            client_paused = data.get("paused")
            # Ensure the client is requesting changes for the currently playing song
            if scheduler_data.get("song_name") == client_song_name:
                current_time = time.time()  # Current time in seconds

                if client_paused:
                    # Handle pause
                    scheduler_data["st"] = "Pause"
                    scheduler_data["c"] = str(client_current_time)  # Update current position (c)
                    scheduler_data["t"] = str(current_time)  # Store the pause timestamp


                else:

                    # Handle play: update state and calculate actual playback time
                    scheduler_data["st"] = "Play"
                    # Calculate the resume time (current position + 5 seconds)
                    current_time = time.time()
                    current_position = float(scheduler_data.get("c", 0))
                    resume_time = current_time + 5
                    # Update playback parameters in the scheduler
                    scheduler_data["t"] = str(resume_time)  # Resume time is 5 seconds from now
                    # Log the playback action
                    print(f"Resuming {client_song_name} at position {current_position}.")

                # Update Redis with modified scheduler data
                redis_client.set("3:sc", json.dumps(scheduler_data))

                # Emit updated scheduler data to all clients
                emit("sync_state", scheduler_data, broadcast=True)
            else:
                print(f"Client attempted to control a different song: {client_song_name}")
            """
            # Handle play/pause behavior
            # pause
            if scheduler_data["st"] == "Play":
                scheduler_data["t"] = str(time.time() + 10)  # Set resume time (10 seconds later)
                current_time = time.time()  # Current time in seconds
                timestamp = float(scheduler_data.get("t", 0))  # Convert to float

                song_name = scheduler_data.get("song_name")
                # Increment current position (c) over time
                current_position = float(scheduler_data.get("c", 0))  # Convert to float
                if current_position < float(scheduler_data.get("d", 0)):  # Ensure current_position is less than the duration
                    scheduler_data["c"] = str(current_time - timestamp)  # Update c based on elapsed time
                    if float(scheduler_data.get("c", 0)) >= float(
                            scheduler_data.get("d", 0)):  # If video reaches its duration, mark it complete
                        scheduler_data["c"] = scheduler_data["d"]
                        scheduler_data["st"] = "Pause"  # Automatically pause when the video ends
                        print(f"{song_name} has finished playing.")

                # If video is currently playing, pause it and store the current position
                scheduler_data["st"] = "Pause"
            else:
                # If the video is paused, set it to play and schedule resume time
                scheduler_data["st"] = "Play"

                #play video at position c at time t


            # Update the Redis key with the new scheduler data
            redis_client.set("3:sc", json.dumps(scheduler_data))

            # Verify the data is being set correctly
            updated_data = redis_client.get("3:sc")
            print(f"Updated scheduler data in Redis: {updated_data}")


            # Emit updated scheduler data to all clients for synchronization
            emit("sync_state", scheduler_data, broadcast=True)
            """
    except Exception as e:
        print(f"Error in play/pause handling: {str(e)}")
        emit("error", {"message": "Error occurred while updating the scheduler."})

@app.route("/")
def index():
    # Render the HTML file (index.html) at the root URL
    return render_template("index2.html")


if __name__ == "__main__":
    # Run the Flask app
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
