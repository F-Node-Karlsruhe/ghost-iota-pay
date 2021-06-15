from flask import Flask, render_template, request, make_response, Response, redirect
import requests
import logging
import jwt	# pip install pyjwt
from datetime import datetime as date
import secrets
import iota_client
import hashlib

app = Flask(__name__.split('.')[0])
logging.basicConfig(level=logging.DEBUG)
# Set it to you domain
LOG = logging.getLogger("app.py")

# register all paying user token hashes
payed_db= {'welcome': set()}

# Url of the ghost blog
URL = 'localhost:2368'

# Ghost Admin API key goes here
key = '60c71d772cc77223dcb90dc8:392420d07ba4c207d530275078de9630a17b0319e98843f50657fa77a429ce5e'

# Split the key into ID and SECRET
id, secret = key.split(':')



@app.route('/<slug>', methods=["GET"])
def proxy(slug):


    # Check if slug exists and add to db
    if slug not in payed_db.keys():
        if requests.get('https://%s/%s' % (URL,slug)).status_code == 200:
            payed_db[slug] = set()
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
	
    
    if has_paid(user_token, slug):
        return deliver_content(slug)

    return make_response(render_template('pay.html'))

def deliver_content(slug):
    # Make an authenticated request to get a posts html
    url = 'http://%s/ghost/api/v3/admin/posts/slug/%s/?formats=html' % (URL, slug)
    headers = {'Authorization': 'Ghost {}'.format(create_token())}
    return requests.get(url, headers=headers).json()['posts'][0]['html']

def has_paid(user_token, slug):

    user_token_hash = hashlib.sha256(user_token.encode('utf-8')).hexdigest()

    if user_token_hash in payed_db[slug]:
        return True

    
    payed_db[slug].add(user_token_hash)
    return False


def get_new_user_id():
    return secrets.token_hex(16)

def create_token():
    iat = int(date.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/v3/admin/'
    }
    return jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)



if __name__ == '__main__':
   app.run()