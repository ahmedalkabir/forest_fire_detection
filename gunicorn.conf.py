""" gunicorn WSGI server configuration """
from multiprocessing import cpu_count
from app import mqtt_service
import threading


def post_worker_init(worker):
    print(f'init somestuff worker {worker}')
    x = threading.Thread(target=mqtt_service.task, args=())
    x.start()

def worker_int(worker):
    print(f'exiting worker {worker}')
    mqtt_service.stop_mqtt()

def max_workers():
    return 2 * cpu_count() + 1

# bind = 'localhost:8000'
workers = max_workers()
preload_app = True