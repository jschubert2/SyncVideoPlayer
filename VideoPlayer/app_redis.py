from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import redis
import json
from datetime import datetime
import time
import threading
from threading import Lock

upd_lock = Lock()
upd = False

def set_upd(value):
    global upd
    with upd_lock:
        upd = value

def get_upd():
    global upd
    with upd_lock:
        return upd


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, message_queue='redis://130.61.189.22:6379')
redis_client = redis.StrictRedis(host='130.61.189.22', port=6379, decode_responses=False)

t_play = 0

@app.route("/")
def index():
    return render_template("index3.html")

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

# Handle client connection
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

# Handle playback updates from the host
@socketio.on("update_state")
def handle_update_state(data):
    try:
        #get data to set scheduler
        #set scheduler in redis
        #emit data to html

        scheduler_data = redis_client.get("3:sc")
        print(scheduler_data)
        if(scheduler_data):
            scheduler_data = json.loads(scheduler_data)
            client_song_name = data.get("song_name")
            client_c = data.get("c")
            client_st = data.get("st")
            print(client_st)

            if(client_st == "Stop"):
                scheduler_data["st"] = "Stop"
                scheduler_data["c"] = str(client_c)
                set_upd(False)
            else:
                print("going into else")
                #scheduler_data["st"] = "Play"
                #think we need a set t and c flag and then a while somewhere where they are continuisly updatet in 3:sc
                set_upd(True)
                t_play = time.time()
                return

            print("we are reaching this point")
            redis_client.set("3:sc", json.dumps(scheduler_data))
        print("we are ALSO reaching this point")
        # Broadcast the updated state to all clients
        emit("sync_state", scheduler_data, broadcast=True)
    except Exception as e:
        print(f"Error in play/pause handling: {str(e)}")
        emit("error", {"message": "Error occurred while updating the scheduler."})

def sc_update():
    while get_upd():
        #print("currently going though sc_update")
        #only set c and t (implementation for palying at c is in html, for t we need to scheduler_data["st"] = "Play" here after 10 seconds)
        scheduler_data = redis_client.get("3:sc")
        if scheduler_data:
            scheduler_data = json.loads(scheduler_data)
            if(float(scheduler_data["t"])+1 <= time.time()):
                scheduler_data["c"] = str(float(scheduler_data["c"])+1)
                scheduler_data["t"] = time.time()

            if (float(scheduler_data["c"]) >= float(scheduler_data["d"])):
                scheduler_data["c"] = scheduler_data["d"]
                scheduler_data["st"] = "Stop"
                emit("sync_state", scheduler_data, broadcast=True)
                set_upd(False)

            if(float(scheduler_data["t"]) >= 5 + t_play): #5 seconds later
                if(scheduler_data["st"] == "Stop"):
                    scheduler_data["st"] = "Play"
                    emit("sync_state", scheduler_data, broadcast=True)

            redis_client.set("3:sc", json.dumps(scheduler_data))

        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=sc_update, daemon=True).start()

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
