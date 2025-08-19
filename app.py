import os
import sys
import traceback
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from py_ballisticcalc import *
import numpy as np
from scipy.interpolate import CubicSpline  # For smooth interpolation with boundary condition

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

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

@app.route('/api/ballistics', methods=['POST'])
def calculate_ballistics():
    try:
        data = request.get_json()
        if data is None or not isinstance(data, dict) or data == {}:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        required_fields = [
            "bc_g7", "muzzle_velocity_fps", "pressure_inhg", "temp_f",
            "wind_speed_mph", "wind_direction_deg", "range_yds"
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        bc_g7 = float(data["bc_g7"])
        muzzle_velocity = float(data["muzzle_velocity_fps"])
        max_range_yds = float(data["range_yds"])
        wind_speed = float(data["wind_speed_mph"])
        wind_direction = float(data["wind_direction_deg"])
        pressure = float(data["pressure_inhg"])
        temp = float(data["temp_f"])

        basicConfig("/home/m/Documents/ballistics_api/.pybc.toml")

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

            print(f"range: {r:.1f} yd | drop_inches: {drop_inches:.2f} | drop_moa: {drop_moa:.3f}")
            
            print(f"DEBUG: range={r}, cs_drop(r)={drop_inches}, cs_wind(r)={windage_val}")

        return jsonify({
            "drop_moa": drop_list[-1],
            "windage_moa": wind_list[-1],
            "time_of_flight_sec": time_list[-1],
            "velocity_at_target_fps": velocity_list[-1],
            "range_yds": [round(r, 1) for r in requested_ranges],
            "drop_array_moa": drop_list,
            "windage_array_moa": wind_list
        })

    except Exception as e:
        log_exception(e)
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)





