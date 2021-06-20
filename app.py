from flask import Flask, render_template, request, make_response, session
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
import time


load_dotenv()

app = Flask(__name__.split('.')[0])

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# create web socket for async communication
socketio = SocketIO(app, async_mode='threading')

socket_session_ids = {}

# restrict the access time for the user
# comment out for infinite
app.permanent_session_lifetime = timedelta(hours=int(os.getenv('SESSION_LIFETIME')))


logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay")


# init iota client
iota = iota_client.Client()

# iota address for transfers
iota_address= os.getenv('IOTA_ADDRESS')

# price per content
price_per_content = int(os.getenv('PRICE_PER_CONTENT'))

# register all paying user token hashes
payed_db = set()

# keep tracl of valid slugs
known_slugs = set()


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



@app.route('/', methods=["GET"])
def welcome():
    return render_template('welcome.html')

@app.route('/<slug>', methods=["GET"])
def proxy(slug):

    # Check if slug exists and add to db
    if slug not in known_slugs:

        if ghost.check_slug_exists(slug):

            known_slugs.add(slug)

            LOG.debug("Added slug %s to db", slug)

        else:

            return make_response('Slug not available')
    

    # Check if user already has cookie and set one 
    if 'iota_ghost_user_token:' + slug not in session:

        session['iota_ghost_user_token:' + slug] = secrets.token_hex(16)       

	
    user_token_hash = hashlib.sha256(str(session['iota_ghost_user_token:' + slug] + slug).encode('utf-8')).hexdigest()
    
    if user_token_hash in payed_db:

        return ghost.get_article(slug)

    return render_template('pay.html', user_token_hash = user_token_hash, iota_address = iota_address, price = price_per_content )


# socket endpoint to receive payment event
# strangely the dict does not persist the ids
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
        event = json.loads(item)

        message = client.get_message_data(json.loads(event['payload'])['messageId'])

        if check_payment(message):
            # this must be easier to access within value transfers
            user_token_hash = bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode()

            payed_db.add(user_token_hash)         

            if user_token_hash in socket_session_ids.keys():

                # emit pamyent received event to the user
                socketio.emit('payment_received', room=socket_session_ids.pop(user_token_hash))

        q.task_done()


def check_payment(message):

    for output in message['payload']['transaction'][0]['essence']['outputs']:

        if output['signature_locked_single']['address'] == iota_address:

            if output['signature_locked_single']['amount'] >= price_per_content:

                return True

    return False

if __name__ == '__main__':

        # sadly this all has to run in the same script
        socketio.start_background_task(mqtt)
        socketio.run(app)

        # Stop server
        LOG.info('Stopping ...')
        q.put(STOP)
        LOG.info('MQTT worker stopped')
        client.disconnect()
        LOG.info('MQTT client stopped')
        q.queue.clear()
        LOG.info('Working queue cleared')