import time
import paho.mqtt.client as mqtt
import json
from sense_hat import SenseHat

# Sense HAT settings
sense = SenseHat()
sense.set_rotation(180)

# Thingspeak MQTT settings
THINGSPEAK_URL = "mqtt.thingspeak.com"
CHANNEL_ID = "1974879"
WRITE_API_KEY = "QAAGUMVHJXNP7NKV"

# Flask API settings
from flask import Flask
app = Flask(__name__)

measured_data = []

@app.route('/get-weather')
def get_weather():
  return json.dumps(measured_data)

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
  print("Connected to Thingspeak with result code "+str(rc))

def on_disconnect(client, userdata, rc):
  if rc != 0:
    print("Unexpected disconnection.")

def on_publish(client, userdata, mid):
  print("Data published to Thingspeak")

# Connect to Thingspeak MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.username_pw_set(CHANNEL_ID, WRITE_API_KEY)
client.connect(THINGSPEAK_URL, 1883, 60)
client.loop_start()

# Main loop
while True:
  # Get sensor data
  temperature = sense.get_temperature()
  humidity = sense.get_humidity()
  pressure = sense.get_pressure()

  # Display sensor data on Sense HAT screen
  message = "Temp: {:.1f}C Humidity: {:.1f}% Pressure: {:.1f}mbar".format(temperature, humidity, pressure)
  sense.show_message(message, scroll_speed=0.05)

  # Save sensor data to list
  data = {"temperature": temperature, "humidity": humidity, "pressure": pressure}
  measured_data.append(data)

  # Publish sensor data to Thingspeak
  client.publish("channels/{:s}/publish/{:s}".format(CHANNEL_ID, WRITE_API_KEY), "field1={:.1f}&field2={:.1f}&field3={:.1f}".format(temperature, humidity, pressure))

  # Sleep for 20 seconds
  time.sleep(20)

# Disconnect from Thingspeak MQTT
client.loop_stop()
client.disconnect()

