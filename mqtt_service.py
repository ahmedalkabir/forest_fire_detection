from mqtt import MQTT
import threading
from sms_request import send_sms_message
import sqlalchemy as sa 
import sqlalchemy.orm as so
from app.models import Action, Thing
from datetime import datetime, timezone
import json

mqtt_service = MQTT('broker.emqx.io', 1883)
engine = sa.create_engine("sqlite:///app.db")

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

def action_processing(msg):
    actions = conn.execute(sa.Select(Action)).all()
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

            


if __name__ == '__main__':
    print('[MQTT SERVICE]')
    conn = engine.connect()

    things =  conn.execute(sa.Select(Thing)).all()
    things_name = [t[1] for t in things]

    mqtt_service.set_action_cb(action_processing)
    mqtt_service.set_subscribers(things_name)

    mqtt_main_thread = threading.Thread(target=mqtt_service.task, args=())
    mqtt_main_thread.start()

