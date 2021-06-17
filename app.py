from flask import Flask, render_template, request, make_response
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

    # Get userId from cookie
    user_token = request.cookies.get('iota_ghost_user_token')

    # Check if user already has cookie and set one 
    if user_token is None:
        resp = make_response(render_template('pay.html'))
        user_token = get_new_user_id()
        resp.set_cookie('iota_ghost_user_token', user_token)
        return resp
	
    user_token_hash = hashlib.sha256(user_token.encode('utf-8')).hexdigest()
    
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