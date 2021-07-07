from flask import session, render_template, redirect, send_from_directory
from . import view
from database.operations import (check_slug,
                                get_access,
                                get_slug_data,
                                get_author_address,
                                access_expired)
from utils.hash import hash_user_token
from config.settings import URL, SESSION_LIFETIME
import secrets
from datetime import datetime, timedelta
from services.ghost.api import get_post_payment, get_post


@view.before_request
def make_session_permanent():   
    # make session persistent
    session.permanent = True

@view.route('/', methods=["GET"])
def welcome():
    return render_template('welcome.html')

@view.route('/favicon.ico', methods=["GET"])
def favicon():
    return send_from_directory('static',
                               'favicon.ico')


@view.route('/<slug>', methods=["GET"])
def proxy(slug):

    # Check if slug exists and add to db
    slug_check = check_slug(slug)

    if slug_check is None:

        return 'Slug not available'

    if slug_check == 'free':

        return redirect('%s/%s' % (URL, slug))
    

    # Check if user already has cookie and set one 
    if 'iota_ghost_user_token:' not in session:

        session['iota_ghost_user_token:'] = secrets.token_hex(16)       


    user_token_hash = hash_user_token(session['iota_ghost_user_token:'], slug)

    access = get_access(user_token_hash, slug)

    if access.exp_date is not None:

        if access.exp_date > datetime.utcnow():

            return get_post(slug, access.exp_date)

        return render_template('expired.html',
                                exp_date = access_expired(user_token_hash).strftime('%d.%m.%y %H:%M UTC'))

    slug_info = get_slug_data(slug)

    iota_address = get_author_address(slug_info.author_id)

    return get_post_payment(slug, render_template('pay.html',
                                                    user_token_hash = user_token_hash,
                                                    iota_address = iota_address,
                                                    price = access.slug_price,
                                                    exp_date =  (datetime.utcnow() + timedelta(hours = SESSION_LIFETIME))
                                                    .strftime('%d.%m.%y %H:%M UTC')))