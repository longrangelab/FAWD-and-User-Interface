import os
import sys
import traceback
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from py_ballisticcalc import *
import numpy as np
from scipy.interpolate import CubicSpline  # For smooth interpolation with boundary condition
from lora_receiver import start_lora_receiver, get_received_messages
import threading
import time

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Start LoRa receiver
start_lora_receiver()

# Global variables for latest environmental data from LoRa
latest_env_data = {
    'wind_speed_mph': 0.0,
    'wind_direction_deg': 0.0,
    'temperature_f': 70.0,  # Default temperature
    'pressure_inhg': 29.92,  # Default pressure
    'last_updated': 0
}
env_data_lock = threading.Lock()

def update_environmental_data():
    """Background thread to update environmental data from LoRa messages"""
    while True:
        try:
            messages = get_received_messages()
            for msg in messages:
                if isinstance(msg, dict) and 'wind_speed' in msg:
                    # This is JSON data from T-Beam
                    with env_data_lock:
                        latest_env_data['wind_speed_mph'] = msg.get('wind_speed', 0)
                        latest_env_data['wind_direction_deg'] = msg.get('wind_direction', 0)
                        # Note: T-Beam doesn't send temp/pressure, so we keep defaults
                        latest_env_data['last_updated'] = time.time()
                        print(f"Updated environmental data from LoRa: Wind {latest_env_data['wind_speed_mph']} mph @ {latest_env_data['wind_direction_deg']}°")
        except Exception as e:
            print(f"Error updating environmental data: {e}")
        time.sleep(1)  # Check for new data every second

# Start the environmental data update thread
env_thread = threading.Thread(target=update_environmental_data, daemon=True)
env_thread.start()

def log_exception(exc):
    print("--------- EXCEPTION ---------", file=sys.stderr)
    traceback.print_exc()
    print("-----------------------------", file=sys.stderr)

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return app.send_static_file('index.html')

@app.route('/api/environment', methods=['GET'])
def get_environment():
    """Get current environmental conditions from LoRa data"""
    with env_data_lock:
        return jsonify({
            'wind_speed_mph': latest_env_data['wind_speed_mph'],
            'wind_direction_deg': latest_env_data['wind_direction_deg'],
            'temperature_f': latest_env_data['temperature_f'],
            'pressure_inhg': latest_env_data['pressure_inhg'],
            'last_updated': latest_env_data['last_updated']
        })

@app.route('/api/ballistics/auto', methods=['POST'])
def calculate_ballistics_auto():
    """Calculate ballistics using automatic LoRa environmental data"""
    try:
        data = request.get_json()
        if data is None or not isinstance(data, dict) or data == {}:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        required_fields = ["bc_g7", "muzzle_velocity_fps", "range_yds"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        # Get environmental data from LoRa
        with env_data_lock:
            wind_speed = latest_env_data['wind_speed_mph']
            wind_direction = latest_env_data['wind_direction_deg']
            pressure = latest_env_data['pressure_inhg']
            temp = latest_env_data['temperature_f']

        bc_g7 = float(data["bc_g7"])
        muzzle_velocity = float(data["muzzle_velocity_fps"])
        max_range_yds = float(data["range_yds"])

        print(f"Using LoRa environmental data: Wind {wind_speed} mph @ {wind_direction}°, Temp {temp}°F, Pressure {pressure} inHg")

        basicConfig()

        weapon = Weapon(sight_height=2)  # inches
        ammo = Ammo(DragModel(bc_g7, TableG7), mv=Velocity.FPS(muzzle_velocity))
        zero_shot = Shot(weapon=weapon, ammo=ammo)

        if wind_speed > 0:
            zero_shot.winds = [Wind(Velocity.MPH(wind_speed), Angular.Degree(wind_direction))]

        calc = Calculator()
        zero_distance = Distance.Yard(100)
        calc.set_weapon_zero(zero_shot, zero_distance)

        shot = calc.fire(zero_shot, trajectory_range=Distance.Yard(max_range_yds), extra_data=True)
        df = shot.dataframe().sort_values('distance')

        distances = np.array(df['distance'])
        drops_in = np.array(df['target_drop'])
        windages = np.array(df['windage_adj'])
        times = np.array(df['time'])
        velocities = np.array(df['velocity'])

        cs_drop = CubicSpline(distances, drops_in, bc_type='natural')
        cs_wind = CubicSpline(distances, windages, bc_type='natural')
        cs_time = CubicSpline(distances, times, bc_type='natural')
        cs_velocity = CubicSpline(distances, velocities, bc_type='natural')

        # Adjust here: sample only starting at 200yd
        N = 101
        START_YARDS = 200
        if max_range_yds < START_YARDS:
            return jsonify({"error": "Range must be at least 200 yards"}), 400
        interval = (max_range_yds - START_YARDS) / (N - 1)
        requested_ranges = [START_YARDS + i * interval for i in range(N)]

        drop_list = []
        wind_list = []
        time_list = []
        velocity_list = []

        for r in requested_ranges:
            drop_inches = float(cs_drop(r))
            windage_val = float(cs_wind(r))
            time_val = float(cs_time(r))
            velocity_val = float(cs_velocity(r))
                
            drop_moa = drop_inches / ((r / 100) * 1.047)

            drop_list.append(round(drop_moa, 3))
            wind_list.append(round(windage_val, 3))
            time_list.append(round(time_val, 3))
            velocity_list.append(round(velocity_val, 1))

        return jsonify({
            "drop_moa": drop_list[-1],
            "windage_moa": wind_list[-1],
            "time_of_flight_sec": time_list[-1],
            "velocity_at_target_fps": velocity_list[-1],
            "range_yds": [round(r, 1) for r in requested_ranges],
            "drop_array_moa": drop_list,
            "windage_array_moa": wind_list,
            "environmental_data": {
                "wind_speed_mph": wind_speed,
                "wind_direction_deg": wind_direction,
                "temperature_f": temp,
                "pressure_inhg": pressure
            }
        })

    except Exception as e:
        log_exception(e)
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

@app.route('/api/lora/messages', methods=['GET'])
def get_lora_messages():
    try:
        messages = get_received_messages()
        parsed_messages = []
        for msg in messages:
            # Parse message: assume format "sender:messageType:payload"
            parts = msg.split(':', 2)
            if len(parts) == 3:
                sender, msg_type, payload = parts
                if msg_type == 'ENV':
                    # Parse environment payload: windSpeed,windMode,windDirection,latitude,longitude,IMUsensitivity
                    env_parts = payload.split(',')
                    if len(env_parts) >= 6:
                        wind_speed = int(env_parts[0])
                        wind_mode = int(env_parts[1])  # hitFlag?
                        wind_direction = int(env_parts[2])
                        latitude = float(env_parts[3])
                        longitude = float(env_parts[4])
                        imu_sensitivity = int(env_parts[5])
                        parsed_messages.append({
                            'type': 'environment',
                            'sender': sender,
                            'wind_speed_mph': wind_speed,
                            'hit_flag': wind_mode,
                            'wind_direction_deg': wind_direction,
                            'latitude': latitude,
                            'longitude': longitude,
                            'imu_sensitivity': imu_sensitivity
                        })
                elif msg_type == 'ALERT':
                    parsed_messages.append({
                        'type': 'alert',
                        'sender': sender,
                        'message': payload
                    })
            else:
                parsed_messages.append({
                    'type': 'raw',
                    'message': msg
                })
        return jsonify({'messages': parsed_messages})
    except Exception as e:
        log_exception(e)
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





