import iota_client
import queue
import json
import logging
from dotenv import load_dotenv
from data import get_iota_listening_addresses, add_to_paid_db, is_own_address
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay-mqtt")


session_lifetime = int(os.getenv('SESSION_LIFETIME'))

# price per content
price_per_content = int(os.getenv('PRICE_PER_CONTENT'))


# The IOTA MQTT broker options
broker_options = {
    'automatic_disconnect': False,
    'timeout': 30,
    'use_ws': True,
    'port': 443,
    'max_reconnection_attempts': 5,
}

# The node mqtt url
node_url = os.getenv('NODE_URL')

class Listener():

    def __init__(self, socketio):

        # hand over the socket object
        self.socketio = socketio

        # link user_token_hashes to session ids
        self.socket_session_ids = {}

        # manual payment checks
        self.manual_pamyent_checks = set()

        # create the iota client
        self.client = iota_client.Client(nodes_name_password=[[node_url]],
                                        mqtt_broker_options=broker_options)

        # The queue to store received events
        self.q = queue.Queue()
        # queue stop object
        self.STOP = object()

    def on_mqtt_event(self, event):
        """Put the received event to queue.
        """
        self.q.put(event)



    def start(self):
        self.client.subscribe_topics(get_iota_listening_addresses(), self.on_mqtt_event)
        self.mqtt_worker()


    def add_listening_address(self, iota_address):
        self.client.subscribe_topic('addresses/%s/outputs' % iota_address, self.on_mqtt_event)


    def mqtt_worker(self):
        """The worker to process the queued events.
        """
        while True:
            item = self.q.get(True)

            # break work routine
            if item is self.STOP: break
            try:
                event = json.loads(item)

                message = self.client.get_message_data(json.loads(event['payload'])['messageId'])

                if self.payment_valid(message):
                    # this must be easier to access within value transfers
                    user_token_hash = bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode()

                    self.unlock_content(user_token_hash)

                    
            
            except Exception as e:
                LOG.warning(e)

            self.q.task_done()


    def unlock_content(self, user_token_hash):

        add_to_paid_db(user_token_hash, session_lifetime)

        # prevent key errors
        if user_token_hash in self.socket_session_ids.keys():

            # emit pamyent received event to the user
            self.socketio.emit('payment_received', room=self.socket_session_ids.pop(user_token_hash))


    def payment_valid(self, message):

        for output in message['payload']['transaction'][0]['essence']['outputs']:

            if is_own_address(output['signature_locked_single']['address']):

                if output['signature_locked_single']['amount'] >= price_per_content:

                    return True

        return False

    
    def manual_payment_check(self, address, user_token_hash):

        # easy checks first to prevent overload
        if user_token_hash not in self.manual_pamyent_checks and is_own_address(address):

            self.manual_pamyent_checks.add(user_token_hash)

            outputs = self.client.find_outputs(addresses=[address])

            for output in outputs:

                message = self.client.get_message_data(output['message_id'])

                if user_token_hash == bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode():

                    if self.payment_valid(message):

                        self.unlock_content(user_token_hash)

            # prevent key errors
            if user_token_hash in self.socket_session_ids.keys():

                # emit pamyent not found
                self.socketio.emit('payment_not_found', room=self.socket_session_ids[user_token_hash])

        self.manual_pamyent_checks.remove(user_token_hash)



    def stop(self):
        self.q.put(self.STOP)
        LOG.info('MQTT worker stopped')
        self.client.disconnect()
        LOG.info('MQTT client stopped')
        self.q.queue.clear()
        LOG.info('Working queue cleared')
