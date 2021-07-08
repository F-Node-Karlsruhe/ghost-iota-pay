import logging
import secrets
from utils.hash import hash_user_token
from services.ghost_api import get_post, get_post_payment
from config.settings import (SESSION_LIFETIME,
                            URL,
                            ADMIN_PANEL)
import os
from services.iota import Listener
from datetime import datetime, timedelta
from flask_socketio import SocketIO
from flask import (Flask,
                    render_template,
                    request,
                    session,
                    send_from_directory,
                    redirect)
from database.db import db
from admin import admin, auth
from database.operations import (check_slug,
                                get_access,
                                get_slug_data,
                                get_author_address,
                                set_socket_session,
                                access_expired,
                                reset_socket_sessions)


app = Flask(__name__.split('.')[0])

app.config.from_object('config.flask')

# create web socket for async communication
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# create itoa listener
iota_listener = Listener(socketio)


# expand default 31 days session lifetime if neccessary
if SESSION_LIFETIME > 744:
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=SESSION_LIFETIME)


logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger("ghost-iota-pay")

connected_clients = 0

@app.before_request
def make_session_permanent():
    
    # make session persistent
    session.permanent = True


@app.route('/', methods=["GET"])
def welcome():
    return render_template('welcome.html')

@app.route('/favicon.ico', methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico')

@app.route('/<slug>', methods=["GET"])
def proxy(slug):

    # Check if slug exists and add to db
    slug_check = check_slug(slug, iota_listener)

    if slug_check is None:

        return 'Slug not available'

    if slug_check == 'free':

        return redirect('%s/%s' % (URL, slug))
    

    # Check if user already has cookie and set one 
    if 'iota_ghost_user_token:' not in session:

        session['iota_ghost_user_token:'] = secrets.token_hex(16)       


    user_token_hash = hash_user_token(session['iota_ghost_user_token:'], slug)

    access = get_access(user_token_hash, slug)

    if access.exp_date is not None:

        if access.exp_date > datetime.utcnow():

            return get_post(slug, access.exp_date)

        return render_template('expired.html',
                                exp_date = access_expired(user_token_hash).strftime('%d.%m.%y %H:%M UTC'))

    slug_info = get_slug_data(slug)

    iota_address = get_author_address(slug_info.author_id)

    return get_post_payment(slug, render_template('pay.html',
                                                    user_token_hash = user_token_hash,
                                                    iota_address = iota_address,
                                                    price = access.slug_price,
                                                    exp_date =  (datetime.utcnow() + timedelta(hours = SESSION_LIFETIME))
                                                    .strftime('%d.%m.%y %H:%M UTC')))



# socket endpoint to receive payment event
@socketio.on('await_payment')
def await_payment(data):

    global connected_clients

    connected_clients += 1

    set_socket_session(data['user_token_hash'], request.sid)

    if connected_clients < 2:

        socketio.start_background_task(iota_listener.start, app)


@socketio.on('disconnect')
def disconnect():

    global connected_clients

    connected_clients -= 1

    if connected_clients < 1:

        LOG.info('%s connected clients. Stopping MQTT ...', connected_clients)

        connected_clients = 0

        reset_socket_sessions()

        socketio.start_background_task(iota_listener.stop)

    


# socket endpoint for manual check on payment
@socketio.on('check_payment')
def check_payment(data):

    socketio.start_background_task(iota_listener.manual_payment_check, app, data['iota_address'], data['user_token_hash'])





if __name__ == '__main__':
        db.init_app(app)

        with app.app_context():
            db.create_all()

        if ADMIN_PANEL:
            admin.init_app(app)
            auth.init_app(app)

        socketio.run(app, host='0.0.0.0')

        # Stop server
        LOG.info('Stopping ...')
        iota_listener.stop()
        
            