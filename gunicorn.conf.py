""" gunicorn WSGI server configuration """
from multiprocessing import cpu_count
import threading
from app import mqtt_service
from mqtt_service import MQTTService
import multiprocessing

mqtt_internal_service = MQTTService('')


def post_worker_init(worker):
    print(f'init somestuff worker {worker}')
    x = threading.Thread(target=mqtt_service.task, args=())
    x.start()

def worker_int(worker):
    print(f'exiting worker {worker}')
    mqtt_service.stop_mqtt()

def on_starting(server):
    mqtt_internal_service.start()
    pass

def on_exit(server):
    mqtt_internal_service.stop()
    pass
    


def max_workers():
    return 2 * cpu_count() + 1

# bind = 'localhost:8000'
workers = max_workers()
preload_app = True