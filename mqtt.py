import paho.mqtt.client as mqtt
import queue
from threading import Event
import ast

from abc import ABC, abstractmethod
from typing import List, Dict

class IChannel(ABC):

    @abstractmethod
    def update(self, msg):
        pass

class Channel:
    def __init__(self, topic, payload_parser=None) -> None:
        self.topic = topic
        self.queue = queue.Queue(maxsize=10)
        self._receiving = False
        self._message = None
        self._new = False
        self._new_message = Event()
        self._payload_parser = payload_parser

    def put(self, value):
        if self._receiving:
            self.queue.put(value, block=False)

    def get(self, timeout = None):
        self._new_message.wait(timeout)
        self._new_message.clear()
        return self._message
    
    def receiving(self, status):
        self._receiving = status

    def notify(self, msg):
        # parse the payload
        if self._payload_parser is None:
            self._message = msg
        else:
            self._message = self._payload_parser(msg)

        self._new_message.set()

    def __repr__(self) -> str:
        return f'<Channel {self.topic}>'

    

class MQTT:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.queue = queue.Queue(maxsize=10)

        self.running = Event()

        # self._channels: List[Channel] = []
        self._channels: Dict[Channel] = {}

    def connect(self):
        print('[connect to mqtt broker]')
        self.client.connect(self.host, self.port)

    def loop(self):
        self.client.loop_forever()

    def task(self):
        print('[TASK]')
        self.connect()
        self.client.loop_start()
        self.running.set()

        while self.running.is_set():
            pass
        
        print('[GETOUT of TASK]')

    def stop_mqtt(self):
        print('[MQTT SERVICE STOPPED]')
        self.running.clear()
        self.client.loop_stop()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        # self.client.subscribe('/car_1')
        pass

    def on_message(self, client: mqtt.Client, userdata, msg):
        msg_payload = {
            'topic': msg.topic,
            'msg': msg.payload
        } 
        self._channels[msg.topic].notify(msg_payload)

    def subscribe_to(self, topic, payload_parser=None):
        topic_str = '/' + topic
        # check if is subscribed, if so 
        # return back the channel
        if self._channels.get(topic_str):
            return self._channels[topic_str]
        else:
            self.client.subscribe(topic_str)
            channel = Channel(topic=topic_str, payload_parser=payload_parser)

            self._channels[topic_str] = channel
            return channel



        