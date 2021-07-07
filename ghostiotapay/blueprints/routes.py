from flask import session, redirect, url_for, render_template, send_from_directory
from . import view


@view.before_request
def make_session_permanent():   
    # make session persistent
    session.permanent = True

@view.route('/', methods=["GET"])
def welcome():
    return render_template('welcome.html')

@view.route('/favicon.ico', methods=["GET"])
def favicon():
    return send_from_directory('static', 'favicon.ico')

@view.route('/<slug>', methods=["GET"])
def proxy(slug):
    return None