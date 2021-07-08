from datetime import datetime
import iota_client
import queue
import json
import logging
from datetime import datetime, timedelta
from config.settings import ALLOW_DUST, SESSION_LIFETIME, NODE_URL, DUST_SEED

from database.operations import get_iota_listening_addresses, add_access, is_own_address, get_socket_session, get_slug_price_for_hash

IOTA_DUST = 1000000


logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay")


# The IOTA MQTT broker options
broker_options = {
    'automatic_disconnect': False,
    'timeout': 30,
    'use_ws': True,
    'port': 443,
    'max_reconnection_attempts': 5,
}

def disable_dust():

    global ALLOW_DUST

    ALLOW_DUST = False


class Listener():

    def __init__(self, socketio):

        # hand over the socket object
        self.socketio = socketio

        # manual payment checks
        self.manual_payment_checks = set()

        # create the iota client
        self.client = iota_client.Client(nodes_name_password=[[NODE_URL]],
                                        mqtt_broker_options=broker_options)

        # The queue to store received events
        self.q = queue.Queue()
        # queue stop object
        self.STOP = object()

    def on_mqtt_event(self, event):
        """Put the received event to queue.
        """
        self.q.put(event)



    def start(self, app):
        with app.app_context():
            self.client.subscribe_topics(get_iota_listening_addresses(), self.on_mqtt_event)
        LOG.info(' started listening ...')
        self.mqtt_worker(app)


    def add_listening_address(self, iota_address):
        '''
        Adds an iota_address to the topics of the mqtt listener
        '''

        self.client.subscribe_topic('addresses/%s/outputs' % iota_address, self.on_mqtt_event)


    def mqtt_worker(self, app):
        """The worker to process the queued events.
        """
        with app.app_context():

            while True:
                item = self.q.get(True)

                # break work routine
                if item is self.STOP: break
                try:
                    event = json.loads(item)

                    message = self.client.get_message_data(json.loads(event['payload'])['messageId'])

                    # this must be easier to access within value transfers
                    user_token_hash = bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode()

                    if self.payment_valid(message, user_token_hash):

                        self.unlock_content(user_token_hash)
                
                except Exception as e:
                    LOG.error(e)

                self.q.task_done()


    def unlock_content(self, user_token_hash, exp_time=None):
        '''
        Sends the user_token_hash to the db with the right expiration time and informs the user via socket
        '''

        if exp_time is None:

            exp_time = datetime.utcnow() + timedelta(hours = SESSION_LIFETIME)
        
        add_access(user_token_hash, exp_time)

        # prevent key errors
        socket_session = get_socket_session(user_token_hash)
            
        if socket_session:

            # emit pamyent received event to the user
            self.socketio.emit('payment_received', room=socket_session)


    def payment_valid(self, message, user_token_hash):
        '''
        Check if the right amount arrived on the rigth address
        '''

        for output in message['payload']['transaction'][0]['essence']['outputs']:

            if output['signature_locked_single']['amount'] >= get_slug_price_for_hash(user_token_hash):

                return True

        return False

    
    def manual_payment_check(self, app, address, user_token_hash):
        '''
        Triggers a crawl on the designated address to find a payment in the past and add it to the db
        '''
        with app.app_context():
            # easy checks first to prevent overload
            if user_token_hash not in self.manual_payment_checks and is_own_address(address):

                self.manual_payment_checks.add(user_token_hash)

                outputs = self.client.find_outputs(addresses=[address])

                for output in outputs:

                    try:

                        message = self.client.get_message_data(output['message_id'])

                        if user_token_hash == bytes(message['payload']['transaction'][0]['essence']['payload']['indexation'][0]['data']).decode():

                            if self.payment_valid(message, user_token_hash):

                                exp_time = self.get_payment_expiry(output['message_id'])

                                if exp_time > datetime.utcnow():

                                    self.unlock_content(user_token_hash, exp_time)

                                    self.manual_payment_checks.remove(user_token_hash)

                                    return

                    except Exception:
                        pass

                # prevent key errors
                socket_session = get_socket_session(user_token_hash)
                
                if socket_session:

                    # emit pamyent not found
                    self.socketio.emit('payment_not_found', room=socket_session)

                self.manual_payment_checks.remove(user_token_hash)

    def get_payment_expiry(self, message_id):
        '''
        Fetches the tangle to get the timestamp of the milstone referencing the message
        '''

        milestone_index = self.client.get_message_metadata(message_id)['referenced_by_milestone_index']

        message_timestamp = datetime.fromtimestamp(self.client.get_milestone(milestone_index)['timestamp'])

        return message_timestamp + timedelta(hours = SESSION_LIFETIME)



    def stop(self):
        '''
        Stops the iota listener gracefully
        '''
        self.client.unsubscribe()
        self.client.disconnect()
        LOG.debug('MQTT client stopped')
        self.q.put(self.STOP)
        LOG.debug('MQTT worker stopped')
        self.q.queue.clear()
        LOG.debug('Working queue cleared')
        LOG.info(' stopped listening')



class DustManager():

    def __init__(self):

        if DUST_SEED is None:
            raise Exception('Canot allow dust without giving a dust seed')
        
        self.seed = DUST_SEED

        self.client = iota_client.Client(nodes_name_password=[[NODE_URL]])

        self.balance = self.client.get_balance(self.seed)

        self.dust_address = self.client.get_unspent_address(self.seed)[0]

        if self.balance < IOTA_DUST:
            LOG.error('Not enough funds to allow dust!')
            LOG.error('Please transfer at least %s IOTA to address %s', (IOTA_DUST, self.dust_address))
            disable_dust()          

        self.number_of_dust_transactions = int(self.balance / 100000)

    def transaction_received(self, amount, author_id):
        pass

    def get_dust_address(self):
        return self.dust_address
