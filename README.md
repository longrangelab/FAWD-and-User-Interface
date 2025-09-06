#F.A.W.D

This project provides a Flask-based API for ballistic calculations using [py-ballisticcalc](https://github.com/username/py-ballisticcalc) and serves a simple frontend interface for interacting with the API.

---

## Project Structure

├── FAWD-and-User-Interface/
│ ├── app.py # Flask API backend
│ ├── requirements.txt # Python dependencies
│ ├── file.pybc.toml # Configuration for py-ballisticcalc
│ └── static/
│ └── index.html # Frontend UI
├── setup_ballistics_api.sh # Setup script for environment and dependencies
├── README.md # This file
└── .gitignore

---

## Setup Instructions

Download the ZIP archive, unzip in documents folder, - open a new terminal in the root of the project folder, and run  `chmod +x setup_ballistics_api.sh` to make the shell script executable, then run the the setup script  `./setup_ballistics_api.sh` in the same terminal to install system dependencies, create a virtual environment, install Python packages, and set up the project structure:

This will:

- Install Python 3 and related tools
- Create a Python virtual environment in  `FAWD-and-User-Interface/venv` 
- Install Python packages listed in `requirements.txt`
- Create the Flask API app if not present
- Copy `index.html` to the static folder for frontend serving

---

## Running the API

Activate the virtual environment and start the Flask server:

 `cd FAWD-and-User-Interface` 
 `source venv/bin/activate` 
 `python app.py` 

The API will be accessible at `http://0.0.0.0:5000`.

---

## Frontend Usage

Open your browser and navigate to:

http://localhost:5000/static/index.html

The frontend allows you to:

- Place shooter and target markers on the map
- Adjust marker positions by dragging
- Fetch current weather data for ballistic calculations
- Download map tiles for offline use

---

## Configuration

### Environment Variables

The application supports the following environment variables for configuration:

- `SIGHT_HEIGHT`: Sight height in inches (default: 2.0)
- `ZERO_DISTANCE`: Zero distance in yards (default: 100.0) 
- `MIN_RANGE`: Minimum calculation range in yards (default: 200.0)
- `MAX_RANGE`: Maximum calculation range in yards (default: 2000.0)
- `CALCULATION_POINTS`: Number of calculation points (default: 101)
- `FLASK_DEBUG`: Enable debug mode (default: false)
- `FLASK_HOST`: Flask host address (default: 0.0.0.0)
- `FLASK_PORT`: Flask port (default: 5000)

### Ballistic Configuration

Adjust ballistic calculation units and parameters in:

.pybc.toml

## Dependencies

Main Python packages (also in `requirements.txt`):

- Flask >=3.0.3
- flask-cors >=5.0.0  
- py-ballisticcalc[exts] >=2.1.0
- py-ballisticcalc[charts] >=2.1.0
- numpy >=2.1.0
- scipy >=1.14.0
- requests >=2.32.0

---

## API Endpoints

### Health Check
`GET /health` - Returns API status and configuration

### Ballistic Calculation  
`POST /api/ballistics` - Calculate ballistic trajectory

**Request Body:**
```json
{
  "bc_g7": 0.5,
  "muzzle_velocity_fps": 2800,
  "pressure_inhg": 29.92,
  "temp_f": 68,
  "wind_speed_mph": 10,
  "wind_direction_deg": 90,
  "range_yds": 800
}
```

**Response:**
```json
{
  "drop_moa": -16.743,
  "windage_moa": 0.828,
  "time_of_flight_sec": 0.99,
  "velocity_at_target_fps": 2100.1,
  "range_yds": [200.0, 206.0, ...],
  "drop_array_moa": [-5.2, -5.8, ...],
  "windage_array_moa": [0.3, 0.35, ...]
}
```

---

## Notes

- Make sure Python 3 is installed on your system.
- The setup script assumes a Debian-based system with `apt-get`.
- Customize `app.py` and frontend as needed for additional features.

---

Feel free to open issues or contribute via pull requests!

