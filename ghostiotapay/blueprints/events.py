from ghostiotapay.extensions import socketio
from flask import request

from database.operations import set_socket_session




# socket endpoint to receive payment event
@socketio.on('await_payment')
def await_payment(data):

    set_socket_session(data['user_token_hash'], request.sid)
    


# socket endpoint for manual check on payment
@socketio.on('check_payment')
def await_payment(data):

    socketio.start_background_task(iota_listener.manual_payment_check, data['iota_address'], data['user_token_hash'])