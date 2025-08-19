#F.A.W.D

This project provides a Flask-based API for ballistic calculations using [py-ballisticcalc](https://github.com/username/py-ballisticcalc) and serves a simple frontend interface for interacting with the API.

---

## Project Structure
ballistics_api_project/
├── ballistics_api/
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

Download the ZIP archive, unzip in documents folder, and Run the setup script './setup_ballistics_api.sh' to install system dependencies, create a virtual environment, install Python packages, and set up the project structure:

This will:

- Install Python 3 and related tools
- Create a Python virtual environment in `ballistics_api/venv`
- Install Python packages listed in `requirements.txt`
- Create the Flask API app if not present
- Copy `index.html` to the static folder for frontend serving

---

## Running the API

Activate the virtual environment and start the Flask server:

'cd ballistics_api'
'source venv/bin/activate'
'python app.py'

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

Adjust ballistic calculation units and parameters in:

ballistics_api/file.pybc.toml

## Dependencies

Main Python packages (also in `requirements.txt`):

- Flask 3.0.3
- flask-cors 5.0.0
- py-ballisticcalc 1.0.1
- numpy 2.1.0
- scipy 1.14.0

---

## Notes

- Make sure Python 3 is installed on your system.
- The setup script assumes a Debian-based system with `apt-get`.
- Customize `app.py` and frontend as needed for additional features.

---

Feel free to open issues or contribute via pull requests!

