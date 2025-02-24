import network
import time
import machine
import dht
import urequests
import ujson
import time

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True) 
    wlan.connect(ssid, password) 

    for _ in range(20):
        if wlan.isconnected():
            print("Connected to Wi-Fi:", wlan.ifconfig())
            return wlan.ifconfig()
        time.sleep(1)
    
    print("Failed to connect to Wi-Fi")
    return None	

WIFI_SSID = ""
WIFI_PASSWORD = ""

connect_wifi(WIFI_SSID, WIFI_PASSWORD)

PIR_PIN = 13
DHT_PIN = 15
pir = machine.Pin(PIR_PIN, machine.Pin.IN)
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

API_URL = "http://your-server-ip:5000/api/sensors"

def get_sensor_data():
    global noMotion, haveMotion
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    motion = pir.value()
    if motion==0:
        noMotion = 1
        haveMotion = 0
    else:
        noMotion = 0
        haveMotion = 1

    return {
        "temperature": temperature,
        "humidity": humidity,
        "noMotion": noMotion,
        "haveMotion": haveMotion
    }

while True:
    data = get_sensor_data()
    print("Sending data:", data)

    try:
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(API_URL, data=ujson.dumps(data), headers=headers)
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Failed to send data:", str(e))

    time.sleep(5)