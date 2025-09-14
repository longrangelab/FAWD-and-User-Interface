# F.A.W.D - Ballistics Calculator with LoRa Integration

This project provides a Flask-based API for ballistic calculations using [py-ballisticcalc](https://github.com/o-murphy/py-ballisticcalc) and serves a simple frontend interface for interacting with the API. Now includes **LoRa integration** with T-Beam devices!

---

## 🚀 New Features - LoRa Integration

### What's New
- **Automatic Environmental Data**: Real-time wind speed/direction from LoRa targets
- **T-Beam USB Integration**: Connect T-Beam directly to Raspberry Pi via USB
- **Live Ballistics**: Automatic calculations using live environmental conditions
- **JSON Data Protocol**: Standardized communication between T-Beam and Pi

### Hardware Setup
1. **T-Beam** (ESP32 LoRa device) - receives LoRa data from targets
2. **USB Cable** - connects T-Beam to Raspberry Pi
3. **Raspberry Pi** - runs the ballistics API and receives data from T-Beam

---

## Project Structure

├── FAWD-and-User-Interface/
│ ├── app.py # Flask API backend with LoRa integration
│ ├── lora_receiver.py # USB serial receiver for T-Beam data
│ ├── requirements.txt # Python dependencies (updated)
│ ├── file.pybc.toml # Configuration for py-ballisticcalc
│ └── static/
│ └── index.html # Frontend UI
├── setup_ballistics_api.sh # Setup script for environment and dependencies
├── README.md # This file
└── .gitignore

---

## Setup Instructions

### 1. Hardware Connection
1. Connect T-Beam to Raspberry Pi via USB cable
2. Ensure T-Beam is programmed with the updated firmware (see T-Beam setup below)
3. Note the USB serial port (typically `/dev/ttyACM0` or `/dev/ttyUSB0`)

### 2. Software Setup
Download the ZIP archive, unzip in documents folder, open a new terminal in the root of the project folder, and run:

```bash
chmod +x setup_ballistics_api.sh
./setup_ballistics_api.sh
```

This will:
- Install Python 3 and related tools
- Create a Python virtual environment in `FAWD-and-User-Interface/venv`
- Install Python packages listed in `requirements.txt`
- Create the Flask API app with LoRa integration
- Copy `index.html` to the static folder for frontend serving

---

## T-Beam Firmware Setup

### Required Changes to T-Beam Code
The T-Beam needs to be updated to forward LoRa data via USB serial. Add this function to your T-Beam `main.cpp`:

```cpp
// Forward LoRa data to Raspberry Pi via USB serial
void forwardDataToPi(String sourceId, int windSpeed, int windMode, int windDirection,
                    double latitude, double longitude, int imu, String hitMessage,
                    float rssi, float snr) {
    String jsonMessage = "{";
    jsonMessage += "\"source_id\":\"" + sourceId + "\",";
    jsonMessage += "\"wind_speed\":" + String(windSpeed) + ",";
    jsonMessage += "\"wind_mode\":" + String(windMode) + ",";
    jsonMessage += "\"wind_direction\":" + String(windDirection) + ",";
    jsonMessage += "\"latitude\":" + String(latitude, 6) + ",";
    jsonMessage += "\"longitude\":" + String(longitude, 6) + ",";
    jsonMessage += "\"imu\":" + String(imu) + ",";
    jsonMessage += "\"hit_message\":\"" + hitMessage + "\",";
    jsonMessage += "\"rssi\":" + String(rssi, 1) + ",";
    jsonMessage += "\"snr\":" + String(snr, 1);
    jsonMessage += "}\n";
    Serial.println(jsonMessage);
}
```

Call this function after parsing protobuf messages in your LoRa receive handler.

---

## Running the API

Activate the virtual environment and start the Flask server:

```bash
cd FAWD-and-User-Interface
source venv/bin/activate
python app.py
```

The API will be accessible at `http://0.0.0.0:5000`.

---

## API Endpoints

### New LoRa-Integrated Endpoints

#### `GET /api/environment`
Returns current environmental conditions from LoRa data:
```json
{
  "wind_speed_mph": 5.2,
  "wind_direction_deg": 270,
  "temperature_f": 70.0,
  "pressure_inhg": 29.92,
  "last_updated": 1640995200.0
}
```

#### `POST /api/ballistics/auto`
Calculate ballistics using automatic LoRa environmental data:
```json
{
  "bc_g7": 0.223,
  "muzzle_velocity_fps": 2600,
  "range_yds": 1000
}
```

### Legacy Endpoints

#### `POST /api/ballistics`
Manual ballistics calculation with user-provided environmental data.

#### `GET /api/lora/messages`
Returns raw LoRa messages received from T-Beam.

---

## Testing the Integration

A test script is provided to verify the complete LoRa integration:

```bash
cd FAWD-and-User-Interface-Lora-integration
source venv/bin/activate
python test_integration.py
```

This will test:
- API server connectivity
- Environmental data endpoint
- Automatic ballistics calculations
- LoRa message reception

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

