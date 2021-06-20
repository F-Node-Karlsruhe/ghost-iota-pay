import requests # pip install requests
import jwt	# pip install pyjwt
from datetime import datetime as date
from dotenv import load_dotenv
import os
import json
from bs4 import BeautifulSoup

load_dotenv()

# Url of the ghost blog
URL = os.getenv('URL')

# Ghost Admin API key goes here
key = os.getenv('GHOST_ADMIN_KEY')

# Split the key into ID and SECRET
id, secret = key.split(':')

def get_article(slug):

    # Make an authenticated request to get a posts html
    api_url = '%s/ghost/api/v3/admin/posts/slug/%s/?formats=html' % (URL, slug)

    url = '%s/%s' % (URL, slug)

    headers = {'Authorization': 'Ghost {}'.format(create_token())}

    data = requests.get(api_url, headers=headers).json()['posts'][0]

    html = BeautifulSoup(requests.get(url).text, "html.parser")

    # clear and prelace content section
    content_section = html.find(class_='gh-content gh-canvas')

    content_section.clear()

    content_section.insert(0, BeautifulSoup(data['html']))

    html = html.prettify()

    # point to base url for original sources
    html = html.replace('href="/', 'href="%s/' % URL).replace('src="/', 'src="%s/' % URL)
    
    return html


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
    return requests.get('%s/%s' % (URL,slug)).status_code == 200
