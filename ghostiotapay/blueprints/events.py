from ghostiotapay.extensions import socketio

# socket endpoint to receive payment event
@socketio.on('connect')
def await_payment(data):

    print('connected')