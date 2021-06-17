from flask import Flask, render_template, request, make_response, session
import logging
import secrets
import hashlib
import iota_mqtt as iota
import ghost_api as ghost
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__.split('.')[0])

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')



logging.basicConfig(level=logging.DEBUG)
# Set it to you domain
LOG = logging.getLogger("iota-ghost-pay")


@app.route('/', methods=["GET"])
def welcome():
    return make_response(render_template('welcome.html'))

@app.route('/<slug>', methods=["GET"])
def proxy(slug):

    # Check if slug exists and add to db
    if slug not in iota.payed_db.keys():

        if ghost.check_slug_exists(slug):

            iota.payed_db[slug] = set()

            LOG.debug("Added slug %s to db", slug)

        else:

            return make_response('Slug not available')
    

    # Check if user already has cookie and set one 
    if 'iota_ghost_user_token' not in session:
        session['iota_ghost_user_token'] = get_new_user_id()
        return make_response(render_template('pay.html'))

	
    user_token_hash = hashlib.sha256(session['iota_ghost_user_token'].encode('utf-8')).hexdigest()
    
    if has_paid(user_token_hash, slug):

        return ghost.deliver_content(slug)

    return make_response(render_template('pay.html', user_token_hash = user_token_hash, iota_address = iota.iota_address, slug = slug, price = iota.PRICE ))


def has_paid(user_token_hash, slug):

    return user_token_hash in iota.payed_db[slug]



def get_new_user_id():
    return secrets.token_hex(16)


if __name__ == '__main__':
    try:
        iota.start()
        app.run()
    except KeyboardInterrupt:
        iota.stop()