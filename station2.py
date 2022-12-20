import thingpeak

channel_id = 123456 # Replace with your channel ID
api_key = 'ABCDEFGHIJKLMNOP' # Replace with your API key

# Read data from the Sense HAT sensors
humidity = sense.get_humidity()
temperature = sense.get_temperature()

# Send the data to ThingSpeak
response = thingpeak.update(channel_id, api_key, field1=humidity, field2=temperature)
print(response.status, response.reason)