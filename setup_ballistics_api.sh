#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

if [ ! -d FAWD-and-User-Interface ]; then
  mkdir -p FAWD-and-User-Interface
fi

cd FAWD-and-User-Interface

python3 -m venv venv
source venv/bin/activate

if [ ! -f requirements.txt ]; then
  cat > requirements.txt <<EOF
Flask>=3
py-ballisticcalc[exts]>=1.0.0
EOF
fi

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f app.py ]; then
  cat > app.py <<EOF
# See py_ballisticcalc unit documentation at:
# https://github.com/o-murphy/py-ballisticcalc

from flask import Flask, request, jsonify
from py_ballisticcalc import Calculator, Shot, Weapon, Ammo, DragModel, Wind, Distance, Velocity, Angular, Atmo

app = Flask(__name__)

@app.route('/api/ballistics', methods=['POST'])
def api_ballistics():
    data = request.json
    try:
        # Refer to py_ballisticcalc documentation for supported units
        g7bc = float(data.get('bc_g7', 0.315))
        mv = float(data.get('velocity', 2792))  # Default in feet per second (fps)
        pressure = float(data.get('pressure', 29.92))  # inHg (inches mercury)
        temperature = float(data.get('temperature', 68))  # Fahrenheit
        wind_speed = float(data.get('windSpeed', 0))      # mph
        wind_dir = float(data.get('windDirection', 0))
        range_yd = float(data.get('range', 875))          # Range in yards

        dragmodel = DragModel(g7bc, table='G7')
        ammo = Ammo(dragmodel, mv=Velocity.FPS(mv))
        weapon = Weapon(sight_height=Distance.Inch(2))
        atmo = Atmo(pressure=pressure, temperature=temperature)
        zero = Shot(weapon=weapon, ammo=ammo, atmo=atmo)
        zero.winds = [Wind(Velocity.MPH(wind_speed), Angular.Degree(wind_dir))]
        calc = Calculator()
        # Convert yards to meters for calculation (1 yard = 0.9144m)
        shot_result = calc.fire(zero, trajectory_range=range_yd * 0.9144, extra_data=True)
        idx = min([i for i, d in enumerate(shot_result.data) if d.travelled_distance.meters >= range_yd * 0.9144], default=-1)
        datum = shot_result.data[idx] if idx >= 0 else shot_result.data[-1]
        return jsonify({
            "drop_inch": float(datum.drop_adjustment.inch) if datum.drop_adjustment else None,
            "windage_inch": float(datum.windage_adjustment.inch) if datum.windage_adjustment else None,
            "time_of_flight_sec": float(datum.time.total_seconds()) if datum.time else None,
            "velocity_fps": float(datum.velocity.fps) if datum.velocity else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF
fi

echo ""
echo "Setup complete. To launch the API run:"
echo "source venv/bin/activate && python app.py"
