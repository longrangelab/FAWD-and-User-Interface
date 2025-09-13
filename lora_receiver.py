import serial
import time
import threading
import RPi.GPIO as GPIO

class sx126x:
    M0 = 22
    M1 = 27
    CFG_REG = [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x17, 0x43, 0x00, 0x00]
    SX126X_UART_BAUDRATE_1200 = 0x00
    SX126X_UART_BAUDRATE_2400 = 0x20
    SX126X_UART_BAUDRATE_4800 = 0x40
    SX126X_UART_BAUDRATE_9600 = 0x60
    SX126X_UART_BAUDRATE_19200 = 0x80
    SX126X_UART_BAUDRATE_38400 = 0xA0
    SX126X_UART_BAUDRATE_57600 = 0xC0
    SX126X_UART_BAUDRATE_115200 = 0xE0

    lora_air_speed_dic = {
        1200: SX126X_UART_BAUDRATE_1200,
        2400: SX126X_UART_BAUDRATE_2400,
        4800: SX126X_UART_BAUDRATE_4800,
        9600: SX126X_UART_BAUDRATE_9600,
        19200: SX126X_UART_BAUDRATE_19200,
        38400: SX126X_UART_BAUDRATE_38400,
        57600: SX126X_UART_BAUDRATE_57600,
        115200: SX126X_UART_BAUDRATE_115200
    }

    lora_buffer_size_dic = {
        32: 0x00,
        64: 0x40,
        128: 0x80,
        240: 0xC0
    }

    lora_power_dic = {
        10: 0x00,
        13: 0x01,
        17: 0x02,
        22: 0x03
    }

    def __init__(self, serial_num, freq, addr, power, rssi, air_speed=2400, net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
        self.rssi = rssi
        self.addr = addr
        self.freq = freq
        self.serial_n = serial_num
        self.power = power
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        self.ser = serial.Serial(serial_num, 9600)
        self.ser.flushInput()
        self.set(freq, addr, power, rssi, air_speed, net_id, buffer_size, crypt, relay, lbt, wor)

    def set(self, freq, addr, power, rssi, air_speed=2400, net_id=0, buffer_size=240, crypt=0, relay=False, lbt=False, wor=False):
        self.send_to = addr
        self.addr = addr
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)
        low_addr = addr & 0xff
        high_addr = addr >> 8 & 0xff
        net_id_temp = net_id & 0xff
        if freq > 850:
            freq_temp = freq - 850
            self.start_freq = 850
            self.offset_freq = freq_temp
        elif freq > 410:
            freq_temp = freq - 410
            self.start_freq = 410
            self.offset_freq = freq_temp
        air_speed_temp = self.lora_air_speed_dic.get(air_speed, None)
        buffer_size_temp = self.lora_buffer_size_dic.get(buffer_size, None)
        power_temp = self.lora_power_dic.get(power, None)
        if rssi:
            rssi_temp = 0x80
        else:
            rssi_temp = 0x00
        l_crypt = crypt & 0xff
        h_crypt = crypt >> 8 & 0xff
        if relay == False:
            self.CFG_REG[3] = high_addr
            self.CFG_REG[4] = low_addr
            self.CFG_REG[5] = net_id_temp
            self.CFG_REG[6] = self.SX126X_UART_BAUDRATE_9600 + air_speed_temp
            self.CFG_REG[7] = buffer_size_temp + power_temp + 0x20
            self.CFG_REG[8] = freq_temp
            self.CFG_REG[9] = 0x43 + rssi_temp
            self.CFG_REG[10] = h_crypt
            self.CFG_REG[11] = l_crypt
        else:
            self.CFG_REG[3] = 0x01
            self.CFG_REG[4] = 0x02
            self.CFG_REG[5] = 0x03
            self.CFG_REG[6] = self.SX126X_UART_BAUDRATE_9600 + air_speed_temp
            self.CFG_REG[7] = buffer_size_temp + power_temp + 0x20
            self.CFG_REG[8] = freq_temp
            self.CFG_REG[9] = 0x03 + rssi_temp
            self.CFG_REG[10] = h_crypt
            self.CFG_REG[11] = l_crypt
        self.ser.flushInput()
        for i in range(2):
            self.ser.write(bytes(self.CFG_REG))
            r_buff = 0
            time.sleep(0.2)
            if self.ser.inWaiting() > 0:
                time.sleep(0.1)
                r_buff = self.ser.read(self.ser.inWaiting())
                if r_buff[0] == 0xC1:
                    pass
                else:
                    pass
                break
            else:
                print("setting fail,setting again")
                self.ser.flushInput()
                time.sleep(0.2)
                print('\x1b[1A', end='\r')
                if i == 1:
                    print("setting fail,Press Esc to Exit and run again")
                    time.sleep(2)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.LOW)
        time.sleep(0.1)

    def send(self, data):
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)
        self.ser.write(data)

    def receive(self):
        if self.ser.inWaiting() > 0:
            time.sleep(0.5)
            r_buff = self.ser.read(self.ser.inWaiting())
            print("receive message from node address with frequence %d,%d.125MHz" % ((r_buff[0] << 8) + r_buff[1], r_buff[2] + self.start_freq), end='\r\n', flush=True)
            print("message is " + str(r_buff[3:-1]), end='\r\n')
            if self.rssi:
                print('\x1b[3A', end='\r')
                print("the packet rssi value: -{0}dBm".format(256 - r_buff[-1:][0]))
            return r_buff[3:-1].decode('utf-8', errors='ignore')
        return None

# Global variables
received_messages = []
lock = threading.Lock()

def receiver_thread():
    node = sx126x(serial_num="/dev/ttyS0", freq=915, addr=0, power=22, rssi=True, air_speed=2400)
    while True:
        msg = node.receive()
        if msg:
            with lock:
                received_messages.append(msg)
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