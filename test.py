import socket
import json
import time
import requests

# UDP server address
UDP_IP = "127.0.0.1"  # Replace with the server's IP address if necessary
UDP_PORT = 5005
CENTER_LAT = 37.310762
CENTER_LON = -78.697992
LAT_RANGE = 1
LON_RANGE = 1

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Fetch plane location data from the OpenSky Network API
def get_plane_locations():
    try:
        # Define the boundaries for the area (latitudes and longitudes)
        lamin = 37.940
        lomin = -79.401
        lamax = 38.695
        lomax = -77.323

        lamin = float(CENTER_LAT-(LAT_RANGE/2))
        print(lamin)
        lomin = CENTER_LON-(LON_RANGE/2)
        lamax = CENTER_LAT+(LAT_RANGE/2)
        lomax = CENTER_LON+(LON_RANGE/2)

        # OpenSky API request URL
        url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
        print(url)
        # Send a GET request to the OpenSky API
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OpenSky API: {e}")
        return {}

# Send location data
def send_location_data():
    plane_data = get_plane_locations()

    # If no plane data is received, exit
    if not plane_data or 'states' not in plane_data:
        print("No plane locations to send.")
        return
    try:
        # Sending plane location data
        for state in plane_data['states']:
            try:
                # Extract relevant data from the response (state information)
                location_data = {
                    "id": state[0],  # ICAO24 address (unique identifier)
                    "lat": state[6],  # Latitude
                    "lng": state[5],  # Longitude
                    "details": {
                        "Type": "Plane",
                        "Tail Number": state[1] if state[1] else "Unknown"  # Tail number if available
                    }
                }

                # Convert the location to JSON format
                json_data = json.dumps(location_data)

                # Send the data to the UDP server
                sock.sendto(json_data.encode('utf-8'), (UDP_IP, UDP_PORT))
                print(f"Sent: {json_data}")

                # Wait for 2 seconds before sending the next location
                time.sleep(0.1)

            except Exception as e:
                print(f"Error sending data: {e}")
    except Exception as e:
        print(f"Error sending data: {e}")

# Main function to start sending location data
if __name__ == "__main__":
    while True:
        send_location_data()
        time.sleep(5)

# Close the socket after sending all data
sock.close()
