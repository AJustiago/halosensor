import machine
import dht
import urequests
import ujson
import time

PIR_PIN = 13
DHT_PIN = 15
pir = machine.Pin(PIR_PIN, machine.Pin.IN)
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))

API_URL = "http://your-server-ip:5000/upload"

def get_sensor_data():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    motion = pir.value()

    return {
        "temperature": temperature,
        "humidity": humidity,
        "motion": motion
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