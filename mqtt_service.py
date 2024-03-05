from mqtt import MQTT, Channel
import threading
from sms_request import send_sms_message
import sqlalchemy as sa 
import sqlalchemy.orm as so
# from app.models import Action, Thing
from app.models import Action, Thing, History
from datetime import datetime, timezone
import json
from typing import List, Dict
from threading import Event
import queue
from sqlalchemy.orm import sessionmaker


def gt(left, right):
    return left > right

def gte(left, right):
    return left >= right

def lt(left, right):
    return left < right

def lte(left, right):
    return left <= right

operations = {'>':gt, '>=':gte, '<':lt, '<=':lte}

map_fields = {'temperature':'temp', 'hum':'humidity', 'gas':'gas'}

class MQTTService:
    def __init__(self, id) -> None:
        print('[MQTTService]')
        self._mqtt_service = MQTT('broker.emqx.io', 1883)
        self._engine = sa.create_engine("sqlite:///app.db")
        self._channels: Dict[Channel] = {}
        self._msg_topic: Dict[str] = {}
        self._queue = queue.Queue(maxsize=10)

        self._new_message = Event()
        self._id = id
        self._session_m = sessionmaker(bind=self._engine)
        self._session = self._session_m()
        


    def start(self):
        self._conn = self._engine.connect()
        things =  self._conn.execute(sa.Select(Thing)).all()
        things_name = [t[1] for t in things]

        self._mqtt_service.set_action_cb(self.action_processing)
        self._mqtt_service.set_on_message_cb(self.outside_on_message)

        self._mqtt_service.set_subscribers(things_name)


        for thing in things_name:
            channel = Channel(topic=thing)
            self._channels[thing] = channel

        print(self._channels)
        mqtt_main_thread = threading.Thread(target=self._mqtt_service.task, args=())
        mqtt_main_thread.start()
 
    def set_value(self, topic):
        self._mm = topic

    def outside_on_message(self, msg):
        print('[outside_on_message]')
        topic = msg['topic'][1:]
        thing = self._session.query(Thing).where(Thing.code_name == topic).all()
        
        self.save_to_histories(msg, thing[0].id)


    def stop(self):
        self._mqtt_service.stop_mqtt()

    def get_channel(self, topic) -> Channel:
        return self._channels.get(topic)

    def action_processing(self, msg):
        actions = self._conn.execute(sa.Select(Action)).all()
        # print(actions)
        # same device
        
        for action in actions:
            if msg['topic'][1:] == action[2]:
                data = json.loads(msg['msg'])
                print(action)
                print(data)
                in_value = data[map_fields['temperature']]
                compare_value = action[7]
                comp_fn = operations[action[6]]
                phone_number = action[4]
                lat = data['lat']
                lng = data['lng']
                if comp_fn(in_value, compare_value):
                    send_sms_message(phone_number, f'ALERT: There is a fire in http://maps.google.com/?ll={lat},{lng}')

    def save_to_histories(self, message, thing_id):
        # read table 
        data = json.loads(message['msg'].decode())
        # n_rows = db.session.query(History.id).count()
        n_rows = self._session.query(History.id).count()
        # delete the history when reach 1500
        if n_rows > 1500:
            self._session.query.query(History).delete()
            self._session.query.commit()

        h = History(lat=data['lat'],lng=data['lng'],
                    temperature=data['temp'], humidity=data['hum'], gas=data['gas'], thing_id=thing_id)
        
        self._session.add(h)
        self._session.commit()

    def __repr__(self) -> str:
        return f'<MQTTService {self._id}>'


if __name__ == '__main__':
    print('[MQTT SERVICE]')






