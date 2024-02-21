from flask import render_template, request, flash, redirect, url_for
from app import app, db, sock, mqtt_service
from app.forms import LoginForm, RegistrationForm
from app.models import User, Thing, History
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit

import ast
import json

testing = 0

@app.route("/")
@app.route("/index")
@login_required
def index():
    devices = db.session.scalars(sa.select(Thing)).all()
    history_query = sa.select(History).order_by(History.timestamp.desc()).limit(10)
    histories_1 = db.session.scalars(history_query).all()
    print(histories_1)
    histories = [{'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}]
    return render_template("index.html", title='Home', devices_v=len(devices), devices=devices, histories=histories_1)

@app.route("/login", methods=['GET', 'POSt'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        print(user)

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)  
      
    return render_template("auth-login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/devices', methods=['GET'])
@login_required
def devices():
    devices = db.session.scalars(sa.select(Thing)).all()
    return render_template('devices.html', devices=devices)

@app.route('/device/<id>', methods=['GET'])
@login_required
def device(id):
    device = db.session.get(Thing, id)
    history_query = sa.select(History).order_by(History.timestamp.desc()).limit(20)
    histories_1 = db.session.scalars(history_query).all()

    histories = [{'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}, 
                 {'location':'32.901467821069986, 13.229698875281889',}]
    return render_template('device.html', device=device, histories=histories_1)


# Websockets 

# to parse messags from devices
def payload_parser(message):
    old_payload: str = message['msg'].decode()
    new_payload = {el[0]:el[1] for el in [el.split(':') 
                                          for el in old_payload.split(',')] }
    message['msg'] = new_payload
    return message

def save_to_histories(message):
    # read table 
    print(message)
    n_rows = db.session.query(History.id).count()
    # delete the history when reach 500
    if n_rows > 500:
        db.session.query(History).delete()
        db.session.commit()

    lat = float(message['msg']['LAT'])
    lng = float(message['msg']['LNG'])
    speed = float(message['msg']['S'])
    temperature = float(message['msg']['T'])
    humidity = float(message['msg']['H'])


    h = History(lat=lat, lng=lng, speed=speed, 
                temperature=temperature, humidity=humidity,
                thing_id=1)
    db.session.add(h)
    db.session.commit()
    # print(message['msg']['LAT'])

@sock.route('/devices')
def websocket_devices(sock):
    while True:
        data = sock.receive()
        print(data)

@sock.route('/device')
def websocket_device(sock):
    print('[websocket_device]')

    # first thing get the car
    device = sock.receive()
    device = ast.literal_eval(device)['device']
    print(f'{sock} - {device}')

    var_channel = mqtt_service.subscribe_to(device + '/st', payload_parser=payload_parser)
    # status_channel = mqtt_service.subscribe_to(device + '/st')

    print(var_channel)
    # print(status_channel)

    while True:
        value = var_channel.get()
        # status = status_channel.get(0)
        save_to_histories(value)
        
        sock.send(json.dumps(value['msg']))
        msg = sock.receive(0)
        if msg == 'CLOSE':
            break
    
    sock.close()