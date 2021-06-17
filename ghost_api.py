import requests # pip install requests
import jwt	# pip install pyjwt
from datetime import datetime as date

# Url of the ghost blog
URL = 'localhost:2368'

# Ghost Admin API key goes here
key = '60c71d772cc77223dcb90dc8:392420d07ba4c207d530275078de9630a17b0319e98843f50657fa77a429ce5e'

# Split the key into ID and SECRET
id, secret = key.split(':')

def deliver_content(slug):
    # Make an authenticated request to get a posts html
    url = 'http://%s/ghost/api/v3/admin/posts/slug/%s/?formats=html' % (URL, slug)
    headers = {'Authorization': 'Ghost {}'.format(create_token())}
    return requests.get(url, headers=headers).json()['posts'][0]['html']

def create_token():
    iat = int(date.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/v3/admin/'
    }
    return jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

def check_slug_exists(slug):
    return requests.get('http://%s/%s' % (URL,slug)).status_code == 200