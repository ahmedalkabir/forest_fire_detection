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
        self._list_of_channels = []

        self._action_fn = None
        self._subscribers = []

        self._on_message_fn = None
        
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
        for sub in self._subscribers:
            self.subscribe_to(sub)

        

    def on_message(self, client: mqtt.Client, userdata, msg):
        msg_payload = {
            'topic': msg.topic,
            'msg': msg.payload
        } 
        self._channels[msg.topic].notify(msg_payload)

        # for action processing
        if self._action_fn:
            self._action_fn(msg_payload)

        if self._on_message_fn:
            self._on_message_fn(msg_payload)

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
            self._list_of_channels.append(channel)
            return channel

    def get_channel(self, topic) -> Channel:
        # topic_str = '/' + topic
        # print(self._channels)
        # return self._channels[topic_str]
        print(len(self._list_of_channels))
        pass

    def set_subscribers(self, things):
        self._subscribers = things

    def set_action_cb(self, fn):
        self._action_fn = fn


    def set_on_message_cb(self, fn):
        self._on_message_fn = fn
        