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

    client.publish("/car_1", "LAT:0.0,LNG:0.0,T:25.6,S:100,H:50.6,ST:T,X:100,Y:400,Z:200")
    # client.publish("/car_2", json.dumps({'temp': 25.6, 'speed': 100, 'status': '', 
    #                           'humidity': 50.6, 'lat':0.0, 'lng':0.0}))
    client.publish("/car_2/status", "connected")
    print("publish to mqtt channel")
    time.sleep(2)