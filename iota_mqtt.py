import iota_client
import json
import queue
import time
import threading
from dotenv import load_dotenv
import os
from app import payment_received

load_dotenv()

# init iota client
iota = iota_client.Client()

# iota address for transfers
iota_address= os.getenv('IOTA_ADDRESS')

# price per content
PRICE = 1000000

# register all paying user token hashes
payed_db= {}


# The node mqtt url
node_url = 'https://chrysalis-nodes.iota.org/' # mainnet if needed

# The queue to store received events
q = queue.Queue()

STOP = object()

# The MQTT broker options
broker_options = {
    'automatic_disconnect': True,
    'timeout': 30,
    'use_ws': True,
    'port': 443,
    'max_reconnection_attempts': 5,
}

client = iota_client.Client(mqtt_broker_options=broker_options)

print(client.get_info())

# The queue to store received events
q = queue.Queue()

# The MQTT broker options
broker_options = {
    'automatic_disconnect': True,
    'timeout': 5,
    'use_ws': True,
    'port': 443,
    'max_reconnection_attempts': 5,
}


def worker():
    """The worker to process the queued events.
    """
    while True:
        item = q.get(True)
        if item is STOP: break
        event = json.loads(item)

        message = client.get_message_data(json.loads(event['payload'])['messageId'])

        if check_payment(message):
            # this must be easier to access within value transfers
            data = bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode()

            slug = data.split(':')[0]
            user_token_hash = data.split(':')[1]

            payed_db[slug].add(user_token_hash)         

            payment_received(user_token_hash)

            print('%s bought slug %s' % (user_token_hash, slug))

        q.task_done()


def on_mqtt_event(event):
    """Put the received event to queue.
    """
    q.put(event)

def check_payment(message):
    for output in message['payload']['transaction'][0]['essence']['outputs']:

        if output['signature_locked_single']['address'] == iota_address:

            if output['signature_locked_single']['amount'] >= PRICE:

                return True

    return False



def stop():
    q.put(STOP)
    time.sleep(1)
    client.disconnect()
    q.queue.clear()

def start():
    client.subscribe_topics(['addresses/%s/outputs' % iota_address], on_mqtt_event)
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
    print('Started listening ...')
