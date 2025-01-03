from flask import Flask, render_template, jsonify, g
import socket
import json
import threading

# Initialize Flask app
app = Flask(__name__)


locations = []
locations_lock = threading.Lock()

def udp_server():
    udp_ip =  "127.0.0.1"
    udp_port = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            location = json.loads(data.decode('utf-8'))
            with locations_lock:  # Use lock to safely modify locations list
                global locations
                locations.append(location)
                print(f"Received location data: {location}")
                print(f"Memory address of locations (get_locations): {id(locations)}")
                print(f"Total locations: {len(locations)}")
        except json.JSONDecodeError:
            print("Received invalid JSON data")

# Start UDP server in a separate thread
thread = threading.Thread(target=udp_server)
thread.daemon = True
thread.start()

# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# API route to get the locations as JSON
@app.route('/api/locations', methods=['GET'])
def get_locations():
    with locations_lock:  # Use lock to safely read the locations list
        # Use g to store locations for the current request context
        g.locations = locations
        print(f"Memory address of locations (get_locations): {id(g.locations)}")
        return jsonify(g.locations)

if __name__ == '__main__':
    app.run(debug=True)
