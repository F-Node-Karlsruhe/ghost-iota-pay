from . import db

from database.models.access import Access
from database.models.authors import Author
from database.models.slugs import Slug

from services.ghost.api import slug_exists, get_post_data
from config.settings import DEFAULT_IOTA_ADDRESS, AUTHOR_ADDRESSES

socket_sessions = {}


def check_slug(slug):

    if __exists(Slug, slug):

        # update iota_address if neccesary
        if AUTHOR_ADDRESSES:

            author = get_post_data(slug)['primary_author']

            if author['location'] is not None:

                if author['location'] != Author.query.get(author['id']).iota_address:

                    update_author_address(author['id'], author['location'])

                    iota_listener.add_listening_address(author['location'])

            else:

                if Author.query.get(author['id']).iota_address != DEFAULT_IOTA_ADDRESS:

                    update_author_address(author['id'], DEFAULT_IOTA_ADDRESS)


        return 'paid'

    else:

        if slug_exists(slug):

            post_data = get_post_data(slug)

            if post_data['visibility'] == 'paid':

                author = post_data['primary_author']

                # add author if not existant
                if not __exists(Author, author['id']):

                    add_author(author['id'], author['name'], author['location'])

                    if author['location'] is not None:

                        iota_listener.add_listening_address(author['location'])

                add_slug(slug, author['id'])

                return 'paid'

            else:

                return 'free'

        return None


def get_access(user_token_hash, slug):

    access = Access.query.get(user_token_hash)

    if not access:

        access = Access(token_hash=user_token_hash, slug=slug)
        db.session.add(access)
        db.session.commit()

    if access.exp_date is None:

        access.slug_price = Slug.query.get(slug).price
        db.session.commit()

    return access

def access_expired(user_token_hash):

    date = Access.query.get(user_token_hash).exp_date
    
    Access.query.get(user_token_hash).exp_date = None

    db.session.commit()

    return date

def get_slug_price_for_hash(user_token_hash):

    return Access.query.get(user_token_hash).slug_price



def set_socket_session(user_token_hash, session_id):

    socket_sessions[user_token_hash] = session_id


def get_socket_session(user_token_hash):

    try:

        return socket_sessions[user_token_hash]

    except KeyError:

        return None


def add_access(user_token_hash, exp_date=None):

    access = Access.query.get(user_token_hash)
    access.exp_date = exp_date
    db.session.commit()


def add_author(author_id, name, iota_address):

    author = Author(id=author_id, name=name, iota_address=iota_address)

    db.session.add(author)
    db.session.commit()

def add_slug(slug, author_id, price=None):

    slug = Slug(slug=slug, author_id=author_id, price=price)
    db.session.add(slug)
    db.session.commit()

def update_author_address(author_id, iota_address):

    Author.query.get(author_id).iota_address = iota_address

    db.session.commit()


def get_slug_data(slug):

    return Slug.query.get(slug)

def get_author_address(author_id):

    if AUTHOR_ADDRESSES:

        return Author.query.get(author_id).iota_address

    return DEFAULT_IOTA_ADDRESS


def get_iota_listening_addresses():
    
    topics = ['addresses/%s/outputs' % DEFAULT_IOTA_ADDRESS]

    if not AUTHOR_ADDRESSES:

        return topics

    for author in db.session.query(Author).all():

        if author.iota_address != DEFAULT_IOTA_ADDRESS:

            topics.append('addresses/%s/outputs' % author.iota_address)

    return topics

def is_own_address(iota_address):

    if iota_address == DEFAULT_IOTA_ADDRESS:

        return True

    return iota_address in [address.iota_address for address in Author.query.distinct(Author.iota_address)]


def __exists(table, key):
    return table.query.get(key) is not None

from services.iota import iota_listener
