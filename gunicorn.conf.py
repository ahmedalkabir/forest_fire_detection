""" gunicorn WSGI server configuration """
from multiprocessing import cpu_count
from app import mqtt_service
import threading


def on_starting(server):
    print('[START MQTT SERVICES]')
    # x = threading.Thread(target=mqtt_service.task, args=())
    # x.start()

def on_exit(server):
    print('[STOP MQTT SERVICES]')
    # mqtt_service.stop_mqtt()

def max_workers():
    return 2 * cpu_count() + 1

bind = 'localhost:8000'
workers = max_workers()
preload_app = True