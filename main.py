from dotenv import load_dotenv
import os

from app import app
from app.mqtt_web import mqtt_service2


if __name__ == '__main__':
    print('[START FLASK APP]')
    mqtt_service2.start()
    app.run(host='0.0.0.0', port=99)
    mqtt_service2.stop()


