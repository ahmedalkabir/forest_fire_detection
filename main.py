from dotenv import load_dotenv
import os

from app import app, mqtt_service
import paho.mqtt.client as mqtt
import threading

def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("connected with result code " + str(rc))

    client.subscribe('/car_1')

def on_message(client: mqtt.Client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def mqtt_function(var):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("broker.emqx.io", 1883, 60)

    client.loop_forever()


if __name__ == '__main__':
    print('[START MQTT SERVICES]')
    mqtt_service.connect()
    x = threading.Thread(target=mqtt_service.task, args=())
    x.start()

    print('[START FLASK APP]')
    app.run(host='0.0.0.0', port=8000)

    mqtt_service.stop_mqtt()