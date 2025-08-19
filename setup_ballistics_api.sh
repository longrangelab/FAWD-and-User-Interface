#!/bin/bash
set -e

sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

if [ ! -d ballistics_api ]; then
  mkdir -p ballistics_api
fi

cd ballistics_api

python3 -m venv venv
source venv/bin/activate

if [ ! -f requirements.txt ]; then
  cat > requirements.txt <<EOF
Flask>=3
py-ballisticcalc>=1.0.0
EOF
fi

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f app.py ]; then
  cat > app.py <<EOF
from flask import Flask, request, jsonify
from py_ballisticcalc import Calculator, Shot, Weapon, Ammo, DragModel, Wind, Distance, Velocity, Angular, Atmo

app = Flask(__name__)

@app.route('/api/ballistics', methods=['POST'])
def api_ballistics():
    data = request.json
    try:
        g7bc = float(data.get('bc_g7', 0.315))
        mv = float(data.get('velocity', 850))
        pressure = float(data.get('pressure', 1013.25))
        temperature = float(data.get('temperature', 20))
        wind_speed = float(data.get('windSpeed', 0))
        wind_dir = float(data.get('windDirection', 0))
        range_m = float(data.get('range', 800))

        dragmodel = DragModel(g7bc, table='G7')
        ammo = Ammo(dragmodel, mv=Velocity.MPS(mv))
        weapon = Weapon(sight_height=Distance.Centimeter(5))
        atmo = Atmo(pressure=pressure, temperature=temperature)
        zero = Shot(weapon=weapon, ammo=ammo, atmo=atmo)

        zero.winds = [Wind(Velocity.KMPH(wind_speed), Angular.Degree(wind_dir))]

        calc = Calculator()
        shot_result = calc.fire(zero, trajectory_range=range_m, extra_data=True)
        idx = min([i for i, d in enumerate(shot_result.data) if d.travelled_distance.meters >= range_m], default=-1)
        datum = shot_result.data[idx] if idx >= 0 else shot_result.data[-1]
        return jsonify({
            "drop_mrad": float(datum.drop_adjustment.mil) if datum.drop_adjustment else None,
            "windage_mrad": float(datum.windage_adjustment.mil) if datum.windage_adjustment else None,
            "time_of_flight": float(datum.time.total_seconds()) if datum.time else None,
            "velocity_at_target": float(datum.velocity.mps) if datum.velocity else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF
fi

echo ""
echo "Setup complete. To launch the API run:"
echo "cd ballistics_api && source venv/bin/activate && python app.py"
