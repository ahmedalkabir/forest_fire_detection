from multiprocessing import Array, Manager, Value
from signal import SIGHUP
import gunicorn.app.base
import argparse
import gunicorn.app.base
import os
import threading
import time
from app import app, data
from mqtt_service import MQTTService

# Custom Gunicorn application: https://docs.gunicorn.org/en/stable/custom.html
class HttpServer(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

        self._mqtt_service = MQTTService('')
        # self._mqtt_service.start()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
    
    def on_exit(self):
        print('hey')


def initialize():
    global data
    data = {}
    data['testing'] = Value('d', 10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument('--num-workers', type=int, default=5)
    parser.add_argument('--port', type=str, default='8080')
    args = parser.parse_args()
    options = {
        'bind': '%s:%s' % ('0.0.0.0', args.port),
        'workers': args.num_workers,
    }
    initialize()

    HttpServer(app, options).run()

