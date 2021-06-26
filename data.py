import logging
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from ghost_api import get_primary_author


load_dotenv()

logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay-db")

PATH = './db/'

# iota address for transfers
IOTA_ADDRESS= os.getenv('IOTA_ADDRESS')

AUTHOR_ADDRESSES= os.getenv('AUTHOR_ADDRESSES') == 'true'

# register all paying user token hashes
paid_db = {}

# try to load paid_db on startup
try:
    with open(PATH + 'paid_db.json','r') as db:
        paid_db = json.load(db)
        LOG.info('Successfully loaded paid_db')
except OSError:
    pass

# dict to differentiate authers and their addresses
authors = {}

try:
    with open(PATH + 'authors.json','r') as db:
        authors = json.load(db)
        LOG.info('Successfully loaded authors')
except OSError:
    pass

# keep track of valid slugs
known_slugs = set()

def is_slug_unknown(slug):
    return  slug not in known_slugs

def add_to_known_slugs(slug):
    known_slugs.add(slug)

def user_token_hash_exists(user_token_hash):
    return user_token_hash in paid_db.keys()

def user_token_hash_valid(user_token_hash):
    return datetime.fromisoformat(paid_db[user_token_hash]) > datetime.now()

def add_to_paid_db(user_token_hash, lifetime):
    paid_db[user_token_hash] = (datetime.now() + timedelta(hours = lifetime)).isoformat()

def pop_from_paid_db(user_token_hash):
    return paid_db.pop(user_token_hash)

def get_exp_date(user_token_hash):
    return datetime.fromisoformat(paid_db[user_token_hash])

def get_iota_listening_addresses():
    
    topics = ['addresses/%s/outputs' % IOTA_ADDRESS]

    for author in authors:

        topics.append('addresses/%s/outputs' % authors[author])

    return topics

def _update_author(id, address, iota_listener):

    authors[id] = address

    iota_listener.add_listening_address(address)


def get_iota_address(slug, iota_listener):

    if AUTHOR_ADDRESSES:

        author = get_primary_author(slug)

        # keep address up to date TODO: check if address is valid
        if author['location']:

            # add if neccessary
            if author['id'] not in authors.keys():

                _update_author(author['id'], author['location'], iota_listener)

            # update if neccessary
            if authors[author['id']] != author['location']:

                _update_author(author['id'], author['location'], iota_listener)
        
            return author['location']

        # return db value if blog address is not set
        if author['id'] in authors.keys():

            return authors[author['id']]

    # return default address from env if above fails
    return IOTA_ADDRESS

# check if the given address belong to the blog
def is_own_address(address):

    if address == IOTA_ADDRESS:

        return True

    return address in authors.values()

# remove all expired entries
def _clear_db():
    now = datetime.now()
    for hash, exp in list(paid_db.items()):
        if datetime.fromisoformat(exp) < now:
            del paid_db[hash]

# safe data befor stop
def stop_db():
    try:
        _clear_db()

        # persist paid hashes
        with open(PATH + 'paid_db.json','w') as db:
            json.dump(paid_db, db)
            LOG.info('Successfully persisted paid_db')
        
        # persist authors
        with open(PATH + 'authors.json','w') as db:
            json.dump(authors, db)
            LOG.info('Successfully persisted authors')
    except OSError as ose:
        LOG.error('Could not safe paid_db', ose)