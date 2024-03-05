import paho.mqtt.client as mqtt
import time
import json 

def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("connected with result code " + str(rc))

    client.subscribe('/car_1')

def on_message(client: mqtt.Client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.emqx.io", 1883, 60)

# client.loop_forever()

client.loop_start()

while True:

    client.publish("/forest_1", json.dumps({'temp': 28.0, 'hum': 67, 'gas': 3000, 'lat': 32.7851238, 'lng': 12.5540404}))
    print("publish to mqtt channel")
    time.sleep(2)