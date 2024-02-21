from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sock import Sock

from mqtt import MQTT

app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
sock = Sock(app)

mqtt_service = MQTT('broker.emqx.io', 1883)

from app import routes, models
