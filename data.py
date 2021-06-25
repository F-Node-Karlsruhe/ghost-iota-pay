import logging
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
# Set it to you domain
LOG = logging.getLogger("ghost-iota-pay-db")

PATH = './db/'

# register all paying user token hashes
paid_db = {}

# try to load db on startup
try:
    with open(PATH + 'paid_db.json','r') as db:
        paid_db = json.load(db)
        LOG.info('Successfully loaded paid_db')
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
        with open(PATH + 'paid_db.json','w') as db:
            json.dump(paid_db, db)
            LOG.info('Successfully persisted paid_db')
    except OSError as ose:
        LOG.error('Could not safe paid_db', ose)