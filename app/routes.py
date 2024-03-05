from flask import render_template, request, flash, redirect, url_for, jsonify
from app import app, db, sock, mqtt_service
from app.forms import LoginForm, RegistrationForm
from app.models import User, Thing, History, Action
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
    username = current_user.username
    email = current_user.email

    return render_template("index.html", title='Home', devices_v=len(devices), devices=devices, username=username, email=email ,histories=histories_1)

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
    username = current_user.username
    email = current_user.email
    devices = db.session.scalars(sa.select(Thing)).all()
    return render_template('devices.html', devices=devices, username=username, email=email)

@app.route('/device/<id>', methods=['GET'])
@login_required
def device(id):
    username = current_user.username
    email = current_user.email


    device = db.session.get(Thing, id)
    history_query = sa.select(History).order_by(History.timestamp.desc()).limit(100)
    histories_1 = db.session.scalars(history_query).all()
    last_update_temp = histories_1[0].temperature
    last_update_hum = histories_1[0].humidity
    last_update_gas = histories_1[0].gas
    last_update_lat = histories_1[0].lat
    last_update_lng = histories_1[0].lng


    return render_template('device.html', 
                           temp = last_update_temp,
                           hum = last_update_hum,
                           gas = last_update_gas,
                           lat = last_update_lat,
                           lng = last_update_lng,
                           device=device, histories=histories_1, username=username, email=email)

@app.route('/add-device', methods=['GET', 'POST'])
@login_required
def add_device():
    username = current_user.username
    email = current_user.email
    if request.method == 'POST':
        code_name = request.values.get('code_name')
        name = request.values.get('name')
        description = request.values.get('description')
        forest_location = request.values.get('forest_location')

        if code_name != "" and name != "" and description != ""  and forest_location != "":

            try:
                thing = Thing(code_name=code_name, name=name, description=description, 
                           location_name=forest_location)
                db.session.add(thing)
                db.session.commit()
                flash(f'{code_name} device has been added to the dashboard', 'success')
            except Exception as ex:
                flash(f'{code_name} device is already added', 'warning')
        else:
            flash("Please Fill all of the fields", 'info')

        return render_template('add_devices.html',  username=username, email=email)
    else:
        return render_template('add_devices.html',  username=username, email=email)


@app.route('/delete-device/<id>', methods=['GET'])
@login_required
def delete_device(id):
    device = db.session.get(Thing, id)
    db.session.delete(device)
    db.session.commit()
    flash(f'{device.code_name} has been deleted', 'success')
    return redirect(url_for('devices'))


@app.route('/actions/', methods=['GET'])
@login_required
def actions():
    username = current_user.username
    email = current_user.email
    actions = db.session.scalars(sa.select(Action)).all()
    return render_template('actions.html',  actions=actions, username=username, email=email)

@app.route('/add-action', methods=['GET', 'POST'])
@login_required
def add_action():
    username = current_user.username
    email = current_user.email
    devices = db.session.scalars(sa.select(Thing)).all()
    if request.method == 'POST':
        device = request.values.get('device')
        name = request.values.get('name')
        type = request.values.get('type')
        destination = request.values.get('destination')
        variable = request.values.get('variable')
        operation = request.values.get('operation')
        value = request.values.get('value', type=float)


        if device != "" and name != "" and type != ""  and destination != "" and variable != "" and operation != "" and value != 0.0:

            try:
                action = Action(name=name, thing_code=device, 
                           type=type, destination=destination, field=variable, operation=operation, value=value)
                db.session.add(action)
                db.session.commit()
                flash(f'{name} action has been added to the dashboard', 'success')
            except Exception as ex:
                flash(f'could not add {name} action {ex}', 'warning')
        else:
            flash("Please Fill all of the fields", 'info')

        return render_template('add_action.html',  devices=devices, username=username, email=email)
    else:
        return render_template('add_action.html',  devices=devices, username=username, email=email)

@app.route('/delete-action/<id>', methods=['GET'])
@login_required
def delete_action(id):
    action = db.session.get(Action, id)
    db.session.delete(action)
    db.session.commit()
    flash(f'{action.name} has been deleted', 'success')
    return redirect(url_for('actions'))

@app.route('/history/<id>', methods=['GET'])
@login_required
def history(id):
    device = db.session.get(Thing, id)
    history_query = sa.select(History).order_by(History.timestamp.desc()).where(History.thing_id == id).limit(100)
    histories_1 = db.session.scalars(history_query).all()
    data = {
        "TIME": [log.timestamp for log in histories_1],
        "temp": [log.temperature for log in histories_1],
        "hum": [log.humidity for log in histories_1],
        "gas": [log.gas for log in histories_1],
    }
    
    return jsonify(data)


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
    global data
    print('[websocket_device]')

    # first thing get the car
    device = sock.receive()
    device = ast.literal_eval(device)['device']
    print(f'{sock} - {device}')

    var_channel = mqtt_service.subscribe_to(device)
    status_channel = mqtt_service.subscribe_to(device + '/status')
    thing = db.session.query(Thing).where(Thing.code_name == device).all()
    print(var_channel)

    while True:
        value = var_channel.get()
        print(f'message - {value}')
        
        sock.send(value['msg'].decode())
        msg = sock.receive(0)
        
        if msg == 'CLOSE':
            break
    
    sock.close()