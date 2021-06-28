import requests # pip install requests
import jwt	# pip install pyjwt
from datetime import datetime as date
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()

# Url of the ghost blog
URL = os.getenv('URL')

# Ghost Admin API key goes here
key = os.getenv('GHOST_ADMIN_KEY')

# Split the key into ID and SECRET
id, secret = key.split(':')

def get_post(slug, exp_date):

    url = '%s/%s' % (URL, slug)

    data = get_post_data(slug)

    html = BeautifulSoup(requests.get(url).text, "html.parser")

    # clear and prelace content section
    content_section = html.find(class_='gh-content gh-canvas')

    content_section.clear()

    # clear pay link button
    html.find('button', {'id':'ghost-iota-pay-link'}).extract()

    # append expire date
    html.find('div', {'class': 'byline-meta-content'}).append(BeautifulSoup(
        '<time class="byline-meta-date"><span class="bull">•</span>Expires %s</time>'
        % exp_date.strftime('%d.%m.%y %H:%M UTC'),
        "html.parser"))

    # insert the actual post content
    content_section.insert(0, BeautifulSoup(data['html'], "html.parser"))

    for img in html.findAll('img', attrs = {'srcset' : True}):

        img['srcset'] = img['srcset'].replace('/content', '%s/content' % URL)

    html = html.prettify()

    # point to base url for original sources
    html = html.replace('href="/', 'href="%s/' % URL).replace('src="/', 'src="%s/' % URL)
    
    return html

def get_post_payment(slug, pay_html):

    url = '%s/%s' % (URL, slug)

    # get base ressource
    html = requests.get(url).text

    # point to base url for original sources
    html = html.replace('href="/', 'href="%s/' % URL).replace('src="/', 'src="%s/' % URL)

    html = BeautifulSoup(html, "html.parser")

    # clear content section
    content_section = html.find('section', {'class':'gh-content gh-canvas'})

    content_section.clear()

    # clear pay link button
    html.find('button', {'id':'ghost-iota-pay-link'}).extract()

    #clear article image
    article_image = html.find('figure', {'class':'article-image'})

    # handle srcset
    for img in html.findAll('img', attrs = {'srcset' : True}):

        img['srcset'] = img['srcset'].replace('/content', '%s/content' % URL)

    if article_image is not None:

        article_image.clear()

    # insert the actual post content
    content_section.insert(0, BeautifulSoup(pay_html, "html.parser"))

    html = html.prettify()

    return html


def get_post_data(slug):

    # Make an authenticated request to get a posts html
    api_url = '%s/ghost/api/v3/admin/posts/slug/%s/?formats=html' % (URL, slug)

    headers = {'Authorization': 'Ghost {}'.format(create_token())}

    return requests.get(api_url, headers=headers).json()['posts'][0]


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

def check_slug_is_paid(slug):
    api_url = '%s/ghost/api/v3/admin/posts/slug/%s' % (URL, slug)

    headers = {'Authorization': 'Ghost {}'.format(create_token())}

    return requests.get(api_url, headers=headers).json()['posts'][0]['visibility'] == 'paid'


def get_primary_author(slug):
    api_url = '%s/ghost/api/v3/admin/posts/slug/%s' % (URL, slug)

    headers = {'Authorization': 'Ghost {}'.format(create_token())}

    return requests.get(api_url, headers=headers).json()['posts'][0]['primary_author']
