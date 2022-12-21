import time
import paho.mqtt.client as mqtt
import json
from sense_hat import SenseHat
import urllib
import http.client
import RPi.GPIO as GPIO
from flask import Flask, request
import threading

sense = SenseHat()
sense.set_rotation(180)

# Thingspeak MQTT settings
THINGSPEAK_URL = "mqtt.thingspeak.com"
CHANNEL_ID = "1974879"
WRITE_API_KEY = "YL1YIZDN7M9R34TW"

app = Flask(__name__)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

temperature = 0
humidity = 0
airpressure = 0

measured_data = []

@app.route('/get-info', methods=['GET'])
def getIp():
    ipaddr = request.remote_addr
    return 'Your IP address is:' + ip_addr

@app.route('/get-weather')
def get_weather():
  return json.dumps(measured_data)

# Main loop
def measure_data():
    global temperature
    global humidity
    global airpressure
    while True:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # Get sensor data
        temperature = sense.get_temperature()
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()
        
        # Sending all data to thingspeak with http.client   
        params = urllib.parse.urlencode({'field1': temperature, 'field2': humidity, 'field3': pressure, 'key':WRITE_API_KEY })
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        conn = http.client.HTTPConnection("api.thingspeak.com:80")
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print (data)

        # Managing the light
        if humidity > 55:
            GPIO.output(7, True)
        else:
            GPIO.output(7, False)

        # Display sensor data on Sense HAT screen
        message = "Temp: {:.1f}C Humidity: {:.1f}% Pressure: {:.1f}mbar".format(temperature, humidity, pressure)
        sense.show_message(message, scroll_speed=0.05)

        # Save sensor data to list
        data = {"time": current_time, "temperature": temperature, "humidity": humidity, "pressure": pressure}
        measured_data.append(data)
        
        print("Done printing")

        # Publish sensor data to Thingspeak
        time.sleep(20)

if __name__ == "__main__":
    thread = threading.Thread(target=measure_data)
    thread.start()
    app.run(port=5000, debug=True)