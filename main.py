import os
import time
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

mongo_db_url = os.getenv("MONGODB_CREDS")
client = MongoClient(mongo_db_url)
db = client.sensordb
collection = db.sensors

UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
DEVICE_LABEL = "halosensor"

def init_mongo_connection():
    """Check MongoDB connection."""
    try:
        client.admin.command('ping')
        print("[INFO] MongoDB connection successful")
    except Exception as e:
        print(f"[ERROR] MongoDB connection failed: {e}")

init_mongo_connection()

def post_request(payload):
    """Send data to Ubidots"""
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}

    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, check credentials and internet connection")
        return False
    
    print("[INFO] Data sent successfully to Ubidots")
    return True

@app.route("/api/", methods=["GET"])
def test():
    return jsonify({"message": "PONG"})

@app.route("/api/sensors", methods=["GET", "POST"])
def handle_sensors():
    """Add new sensor record or retrieve all sensor data."""
    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"error": "Invalid input"}), 400
        print(data)
        
        collection.insert_one(data)
        latest_sensor = collection.find_one(sort=[("_id", -1)])
        if latest_sensor:
            payload = {
                "temperature": latest_sensor.get("temperature", 0),
                "humidity": latest_sensor.get("humidity", 0),
                "noMotion": latest_sensor.get("noMotion", 0),
                "haveMotion": latest_sensor.get("haveMotion", 0)
            }
            post_request(payload)

        return jsonify({"message": "Sensor added and data sent to Ubidots"}), 201

    elif request.method == "GET":
        sensors = list(collection.find({}, {'_id': False}))
        return jsonify(sensors), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
