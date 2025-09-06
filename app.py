import os
import sys
import traceback
import hashlib
from functools import lru_cache
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from py_ballisticcalc import *
import numpy as np
from scipy.interpolate import CubicSpline  # For smooth interpolation with boundary condition

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Initialize ballistics configuration once at startup
try:
    basicConfig()
    print("Ballistics configuration loaded successfully", file=sys.stderr)
except Exception as e:
    print(f"Warning: Failed to load ballistics configuration: {e}", file=sys.stderr)

# Configuration constants with environment variable support
SIGHT_HEIGHT = float(os.environ.get('SIGHT_HEIGHT', '2.0'))  # inches
ZERO_DISTANCE = float(os.environ.get('ZERO_DISTANCE', '100.0'))  # yards
MIN_RANGE = float(os.environ.get('MIN_RANGE', '200.0'))  # yards
MAX_RANGE = float(os.environ.get('MAX_RANGE', '2000.0'))  # yards
CALCULATION_POINTS = int(os.environ.get('CALCULATION_POINTS', '101'))

def log_exception(exc):
    print("--------- EXCEPTION ---------", file=sys.stderr)
    traceback.print_exc()
    print("-----------------------------", file=sys.stderr)

def validate_input_range(value, min_val, max_val, field_name):
    """Validate that a numeric input is within acceptable range"""
    if not (min_val <= value <= max_val):
        raise ValueError(f"{field_name} must be between {min_val} and {max_val}, got {value}")

def create_calculation_key(bc_g7, muzzle_velocity, pressure, temp, wind_speed, wind_direction, max_range_yds):
    """Create a cache key for ballistics calculations"""
    key_string = f"{bc_g7}:{muzzle_velocity}:{pressure}:{temp}:{wind_speed}:{wind_direction}:{max_range_yds}"
    return hashlib.md5(key_string.encode()).hexdigest()

@lru_cache(maxsize=32)  # Cache up to 32 recent calculations
def calculate_ballistics_cached(bc_g7, muzzle_velocity, pressure, temp, wind_speed, wind_direction, max_range_yds):
    """Cached ballistics calculation to avoid redundant computation"""
    
    weapon = Weapon(sight_height=SIGHT_HEIGHT)  # inches
    ammo = Ammo(DragModel(bc_g7, TableG7), mv=Velocity.FPS(muzzle_velocity))
    zero_shot = Shot(weapon=weapon, ammo=ammo)

    if wind_speed > 0:
        zero_shot.winds = [Wind(Velocity.MPH(wind_speed), Angular.Degree(wind_direction))]

    calc = Calculator()
    zero_distance = Distance.Yard(ZERO_DISTANCE)
    calc.set_weapon_zero(zero_shot, zero_distance)

    shot = calc.fire(zero_shot, trajectory_range=Distance.Yard(max_range_yds), extra_data=True)
    df = shot.dataframe().sort_values('distance')

    distances = np.array(df['distance'])
    drops_in = np.array(df['target_drop'])
    windages = np.array(df['windage_adj'])
    times = np.array(df['time'])
    velocities = np.array(df['velocity'])

    return distances, drops_in, windages, times, velocities

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "version": "1.0",
        "config": {
            "sight_height": SIGHT_HEIGHT,
            "zero_distance": ZERO_DISTANCE,
            "min_range": MIN_RANGE,
            "max_range": MAX_RANGE
        }
    })

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

        # Parse and validate inputs
        try:
            bc_g7 = float(data["bc_g7"])
            muzzle_velocity = float(data["muzzle_velocity_fps"])
            max_range_yds = float(data["range_yds"])
            wind_speed = float(data["wind_speed_mph"])
            wind_direction = float(data["wind_direction_deg"])
            pressure = float(data["pressure_inhg"])
            temp = float(data["temp_f"])
            
            # Validate input ranges
            validate_input_range(bc_g7, 0.1, 2.0, "BC G7")
            validate_input_range(muzzle_velocity, 500, 5000, "Muzzle velocity")
            validate_input_range(max_range_yds, MIN_RANGE, MAX_RANGE, "Range")
            validate_input_range(wind_speed, 0, 100, "Wind speed")
            validate_input_range(wind_direction, 0, 360, "Wind direction")
            validate_input_range(pressure, 20, 35, "Atmospheric pressure")
            validate_input_range(temp, -50, 150, "Temperature")
            
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Invalid input values: {str(e)}"}), 400

        # Use cached calculation
        distances, drops_in, windages, times, velocities = calculate_ballistics_cached(
            bc_g7, muzzle_velocity, pressure, temp, wind_speed, wind_direction, max_range_yds
        )

        # Create interpolation splines
        cs_drop = CubicSpline(distances, drops_in, bc_type='natural')
        cs_wind = CubicSpline(distances, windages, bc_type='natural')
        cs_time = CubicSpline(distances, times, bc_type='natural')
        cs_velocity = CubicSpline(distances, velocities, bc_type='natural')

        # Generate output points starting at minimum range
        if max_range_yds < MIN_RANGE:
            return jsonify({"error": f"Range must be at least {MIN_RANGE} yards"}), 400
            
        interval = (max_range_yds - MIN_RANGE) / (CALCULATION_POINTS - 1)
        requested_ranges = [MIN_RANGE + i * interval for i in range(CALCULATION_POINTS)]

        drop_list = []
        wind_list = []
        time_list = []
        velocity_list = []

        for r in requested_ranges:
            drop_inches = float(cs_drop(r))
            windage_val = float(cs_wind(r))
            time_val = float(cs_time(r))
            velocity_val = float(cs_velocity(r))
                
            # Convert drop to MOA (1 MOA = 1.047 inches at 100 yards)
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
            "windage_array_moa": wind_list
        })

    except Exception as e:
        log_exception(e)
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e) if app.debug else "Calculation failed"
        }), 500

if __name__ == "__main__":
    # Production-ready configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    
    print(f"Starting FAWD Ballistics API on {host}:{port}", file=sys.stderr)
    print(f"Debug mode: {debug_mode}", file=sys.stderr)
    print(f"Configuration: sight_height={SIGHT_HEIGHT}in, zero_distance={ZERO_DISTANCE}yd", file=sys.stderr)
    
    app.run(host=host, port=port, debug=debug_mode)

