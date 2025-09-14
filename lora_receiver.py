import serial
import time
import threading
import json

class TBeamSerialReceiver:
    def __init__(self, serial_port="/dev/ttyACM0", baudrate=115200):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        
    def connect(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
            self.connected = True
            print(f"Connected to T-Beam on {self.serial_port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to T-Beam: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
    
    def receive(self):
        if not self.connected or not self.ser:
            return None
            
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Received from T-Beam: {line}")
                    return line
        except serial.SerialException as e:
            print(f"Serial read error: {e}")
            self.connected = False
        except UnicodeDecodeError as e:
            print(f"Decode error: {e}")
            
        return None
    
    def is_connected(self):
        return self.connected and self.ser and self.ser.is_open

# Global variables for received data
received_messages = []
lock = threading.Lock()

def receiver_thread():
    # Try different common USB serial ports for T-Beam
    ports_to_try = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"]
    receiver = None
    
    for port in ports_to_try:
        print(f"Trying to connect to T-Beam on {port}...")
        receiver = TBeamSerialReceiver(serial_port=port, baudrate=115200)
        if receiver.connect():
            print(f"Successfully connected to T-Beam on {port}")
            break
        else:
            print(f"Failed to connect on {port}")
    
    if not receiver or not receiver.is_connected():
        print("ERROR: Could not connect to T-Beam on any USB port")
        print("Make sure T-Beam is connected via USB and serial forwarding is enabled")
        return
    
    print("Starting T-Beam data receiver...")
    
    while True:
        try:
            msg = receiver.receive()
            if msg:
                # Try to parse as JSON
                try:
                    data = json.loads(msg)
                    with lock:
                        received_messages.append(data)
                    print(f"Parsed LoRa data: {data}")
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {msg}")
        except Exception as e:
            print(f"Receiver error: {e}")
            # Try to reconnect
            if not receiver.is_connected():
                print("Connection lost, attempting to reconnect...")
                receiver.connect()
        
        time.sleep(0.1)

def start_lora_receiver():
    thread = threading.Thread(target=receiver_thread)
    thread.daemon = True
    thread.start()

def get_received_messages():
    with lock:
        msgs = received_messages.copy()
        received_messages.clear()
        return msgs

# Legacy compatibility - return sx126x class for any existing code
class sx126x(TBeamSerialReceiver):
    def __init__(self, serial_num, freq, addr, power, rssi, air_speed=2400, net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
        # Ignore LoRa parameters and use USB serial instead
        super().__init__(serial_port="/dev/ttyACM0", baudrate=115200)