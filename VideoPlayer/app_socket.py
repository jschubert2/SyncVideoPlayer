from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Store the playback state
video_state = {
    "timestamp": 0,  # Current playback time in seconds
    "paused": True,  # Playback status
}

@app.route("/")
def index():
    return render_template("index.html")

# Handle client connection
@socketio.on("sync_request")
def handle_sync_request():
    # Send the current video state to the new client
    emit("sync_state", video_state)

# Handle playback updates from the host
@socketio.on("update_state")
def handle_update_state(data):
    global video_state
    video_state = data
    # Broadcast the updated state to all clients
    emit("sync_state", video_state, broadcast=True, include_self=False)

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
