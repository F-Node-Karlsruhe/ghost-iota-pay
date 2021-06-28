import logging
import secrets
import hashlib
import ghost_api as ghost
from dotenv import load_dotenv
import os
import iota
from datetime import datetime, timedelta
from flask_socketio import SocketIO
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
                    stop_db,
                    get_iota_address,
                    get_iota_listening_addresses,
                    is_own_address,
                    get_exp_date)


load_dotenv()

app = Flask(__name__.split('.')[0])

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# create web socket for async communication
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# create itoa listener
iota_listener = iota.Listener(socketio)

session_lifetime = int(os.getenv('SESSION_LIFETIME'))

# price per content
price_per_content = int(os.getenv('PRICE_PER_CONTENT'))

# expand default 31 days session lifetime if neccessary
if session_lifetime > 744:
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=session_lifetime)


logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay")


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

            return ghost.get_post(slug, get_exp_date(user_token_hash))

        return render_template('expired.html',
                                exp_date = datetime.fromisoformat(pop_from_paid_db(user_token_hash)).strftime('%d.%m.%y %H:%M UTC'))

    return ghost.get_post_payment(slug, render_template('pay.html',
                                                        user_token_hash = user_token_hash,
                                                        iota_address = get_iota_address(slug, iota_listener),
                                                        price = price_per_content,
                                                        exp_date =  (datetime.utcnow() + timedelta(hours = session_lifetime))
                                                        .strftime('%d.%m.%y %H:%M UTC')))



# socket endpoint to receive payment event
@socketio.on('await_payment')
def await_payment(data):

    user_token_hash = data['user_token_hash']

    iota_listener.socket_session_ids[user_token_hash] = request.sid


# socket endpoint for manual check on payment
@socketio.on('check_payment')
def await_payment(data):

    socketio.start_background_task(iota_listener.manual_payment_check, data['iota_address'], data['user_token_hash'])





if __name__ == '__main__':

        # sadly this all has to run in the same script to make socketio work with threads
        socketio.start_background_task(iota_listener.start)
        socketio.run(app, host='0.0.0.0')

        # Stop server
        LOG.info('Stopping ...')
        iota_listener.stop()
        stop_db()
        
            