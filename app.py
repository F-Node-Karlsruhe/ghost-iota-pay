import logging
import secrets
import hashlib
import ghost_api as ghost
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_socketio import SocketIO
import iota_client
import json
import queue
from flask import (Flask,
                    render_template,
                    request,
                    make_response,
                    session,
                    send_from_directory,
                    redirect)
from data import (user_token_hash_exists,
                    user_token_hash_valid,
                    is_slug_unknown, 
                    add_to_known_slugs,
                    add_to_paid_db,
                    pop_from_paid_db,
                    stop_db)


load_dotenv()

app = Flask(__name__.split('.')[0])

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# create web socket for async communication
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# link user_token_hashes to session ids
socket_session_ids = {}

session_lifetime = int(os.getenv('SESSION_LIFETIME'))

# expand default 31 days session lifetime if neccessary
if session_lifetime > 744:
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=session_lifetime)


logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay")


# init iota client
iota = iota_client.Client()

# iota address for transfers
iota_address= os.getenv('IOTA_ADDRESS')

# price per content
price_per_content = int(os.getenv('PRICE_PER_CONTENT'))


# The node mqtt url
node_url = os.getenv('NODE_URL')

# The queue to store received events
q = queue.Queue()
# queue stop object
STOP = object()

# The IOTA MQTT broker options
broker_options = {
    'automatic_disconnect': True,
    'timeout': 30,
    'use_ws': True,
    'port': 443,
    'max_reconnection_attempts': 5,
}

# create the iota client
client = iota_client.Client(nodes_name_password=[[node_url]],
                            mqtt_broker_options=broker_options)

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
    if is_slug_unknown(slug):

        if ghost.check_slug_exists(slug):

            if ghost.check_slug_is_paid(slug):

                add_to_known_slugs(slug)

                LOG.debug("Added slug %s to db", slug)

            else:

                # redirect if post is free
                return redirect('%s/%s' % (ghost.URL, slug))

        else:

            return make_response('Slug not available')
    

    # Check if user already has cookie and set one 
    if 'iota_ghost_user_token:' not in session:

        session['iota_ghost_user_token:'] = secrets.token_hex(16)       

	
    user_token_hash = hashlib.sha256(str(session['iota_ghost_user_token:'] + slug).encode('utf-8')).hexdigest()
    
    if user_token_hash_exists(user_token_hash):

        if user_token_hash_valid(user_token_hash):

            return ghost.get_post(slug)
        
        exp_date = pop_from_paid_db(user_token_hash)

        return make_response('Access expired at %s' % exp_date)

    return ghost.get_post_payment(slug, render_template('pay.html', user_token_hash = user_token_hash, iota_address = iota_address, price = price_per_content ))


# socket endpoint to receive payment event
@socketio.on('await_payment')
def await_payment(data):

    user_token_hash = data['user_token_hash']

    socket_session_ids[user_token_hash] = request.sid



def on_mqtt_event(event):
    """Put the received event to queue.
    """
    q.put(event)



def mqtt():
    client.subscribe_topics(['addresses/%s/outputs' % iota_address], on_mqtt_event)
    mqtt_worker()


def mqtt_worker():
    """The worker to process the queued events.
    """
    while True:
        item = q.get(True)

        # break work routine
        if item is STOP: break
        try:
            event = json.loads(item)

            message = client.get_message_data(json.loads(event['payload'])['messageId'])

            if check_payment(message):
                # this must be easier to access within value transfers
                user_token_hash = bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode()

                add_to_paid_db(user_token_hash, session_lifetime)

                if user_token_hash in socket_session_ids.keys():

                    # emit pamyent received event to the user
                    socketio.emit('payment_received', room=socket_session_ids.pop(user_token_hash))
        
        except Exception as e:
            LOG.warning(e)

        q.task_done()


def check_payment(message):

    for output in message['payload']['transaction'][0]['essence']['outputs']:

        if output['signature_locked_single']['address'] == iota_address:

            if output['signature_locked_single']['amount'] >= price_per_content:

                return True

    return False


if __name__ == '__main__':

        # sadly this all has to run in the same script to make socketio work with threads
        socketio.start_background_task(mqtt)
        socketio.run(app, host='0.0.0.0')

        # Stop server
        LOG.info('Stopping ...')
        q.put(STOP)
        LOG.info('MQTT worker stopped')
        client.disconnect()
        LOG.info('MQTT client stopped')
        q.queue.clear()
        LOG.info('Working queue cleared')
        stop_db()
        
            