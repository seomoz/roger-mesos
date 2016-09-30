from flask import Flask, jsonify, request, render_template, redirect, make_response, flash, Response
from flask_restful import abort, Api, Resource
from flask_login import login_user, logout_user, login_required, current_user
from webargs import fields
from webargs.flaskparser import use_args
import os
import json
import logging

from authenticators import FileAuthenticator
from authorizers import FileAuthorizer
from resources import Users, Groups, CanActAsUsers, QuotaBuckets, QuotaAllocations, QuotaUsers
from sessions import login_manager, SessionUser
from logs import ContextualFilter

app = Flask(__name__)
app.config.from_object('config')

api = Api(app)
login_manager.init_app(app)

COOKIE_DOMAIN = os.getenv('SESSION_ID_DOMAIN', None)
ACTAS_COOKIE_NAME = os.getenv('ACTAS_COOKIE_NAME', 'aaadactas')

@app.before_first_request
def setup_logging():
    if not app.debug:
        context_provider = ContextualFilter()
        app.logger.addFilter(context_provider)
        handler = logging.StreamHandler() # sys.stderr
        formatter = logging.Formatter('[%(asctime)-15s] %(levelname)s - ip:%(ip)s - user:%(user_id)s - %(method)s:%(url)s - module:%(module)s|%(lineno)s|%(funcName)s - %(message)s')
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        log_levels = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}
        log_level = os.environ.get('LOG_LEVEL', 'warning')
        app.logger.setLevel(log_levels.get(log_level, logging.NOTSET))

@app.route('/auth')
@login_required
def authorize():
    '''
    This method finds out if the current user is authorized to -
        - perform the action specified in 'method' header
        - on the resource specified in 'URI header'
    The request body and content_type are also required for ths purpose.

    Note:
    Because of the @login_required decorator authentication should be already complete
    using one of the supported methods by the time we reach this method. So, let's just
    worry about authorizaton.
    '''
    user = current_user.get_username()
    actas = _find_actas_from_request(request) or current_user.get_username()

    resource = request.headers.get('URI','')
    data = request.get_data()
    content_type = request.headers.get('content-type', '')
    action = request.headers.get('method', '')

    if action.lower() in [ "get", "head", "connect", "trace" ]:
        app.logger.info("Received {} on {} with user acting as {}".format(action, resource, actas))
    else:
        app.logger.warning("Received {} on {} with user acting as {}".format(action, resource, actas))

    auth_result = FileAuthorizer().instance.authorize(user=user, act_as=actas, resource=resource, data=data, content_type=content_type, action=action)
    if not auth_result:
        if not auth_result.messages:
            abort(403)
        else:
            return json.dumps({'success':False, 'messages':auth_result.messages}), 403, {'ContentType':'application/json'}

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/filter')
@login_required
def filter_response():
    '''
    This method filters the response (body) based on the access the current user has.
    Should typically be called by the proxy (internal) and not from outside.
    '''
    user = current_user.get_username()
    actas = _find_actas_from_request(request) or current_user.get_username()

    resource = request.headers.get('URI','')
    data = request.get_data()

    response = FileAuthorizer().instance.filter_response(resource, data, actas)
    return Response(response=response, status=200, mimetype="application/json")

@app.route('/login', methods=['GET', 'POST'])
def login():
    actas = request.cookies.get(ACTAS_COOKIE_NAME) or request.headers.get("act_as_user")
    redirect_url = request.args.get('next', '/')
    if request.method == 'POST':
        redirect_url = request.form.get('redirect', redirect_url) # Note: if auth succeeds we re-direct to this else we render it to index.html if auth fails
        username = request.form.get('user')
        passw = request.form.get('pass')
        if username and passw:
            if (FileAuthenticator().instance.authenticate(username, passw)):
                session_user = SessionUser.get(username)
                if session_user:
                    login_user(session_user, remember=True)
                    # if the user can act as only one user, auto update actas
                    actaslist = FileAuthorizer().instance.get_canactas_list(current_user.get_username())
                    if len(actaslist) == 1:
                        actas = actaslist[0]
                else:
                    flash('Something didn\'t work! Please re-try with the right credentials.')
                    return make_response(render_template('index.html', **locals()))
            else:
                flash('Authentication failed.')
                return make_response(render_template('index.html', **locals()))
        else:
            actas = request.form.get('act_as')

        if current_user.is_authenticated:
            if not actas:
                actas = current_user.get_username()
            if actas in FileAuthorizer().instance.get_canactas_list(current_user.get_username()):
                # all's well, let's set cookie and redirect
                resp = make_response(redirect(redirect_url or '/'))
                resp.set_cookie(ACTAS_COOKIE_NAME, actas, domain=COOKIE_DOMAIN)
                return resp
            else:
                if actas:
                    flash('Not authorized to act as {}.'.format(actas))
                actas = None
                resp = make_response(render_template('index.html', **locals()))
                _clear_cookies(resp)
                return resp
        else:
            flash('Authentication required.')
            return make_response(render_template('index.html', **locals()))

    if request.args.get('resetactas', 'false').lower() in ['true', '1', 'yes']:
        actas = None

    if not current_user.is_authenticated:
        flash('Please log in.')

    return make_response(render_template('index.html', **locals()))

@app.route('/login/user', methods=['GET'])
def user_details():
    username = ''
    if current_user.is_authenticated:
        username = current_user.get_username()
    return jsonify({ 'username': username })

@app.route('/logout')
def logout():
    logout_user()
    actas = None
    flash('You\'re logged out. Thank you for visiting!')
    resp = make_response(render_template('index.html', **locals()))
    _clear_cookies(resp)
    return resp

def _clear_cookies(resp):
    resp.set_cookie(ACTAS_COOKIE_NAME, '', expires=0, domain=COOKIE_DOMAIN)
    resp.set_cookie(ACTAS_COOKIE_NAME, '', expires=0, domain=None)

def _find_actas_from_request(request):
    return ( request.cookies.get(ACTAS_COOKIE_NAME) or
             request.headers.get("act_as_user") )

api.add_resource(Users, '/api/users')
api.add_resource(Groups, '/api/groups')
api.add_resource(CanActAsUsers, '/api/users/<string:user>/can_act_as')
api.add_resource(QuotaBuckets, '/api/quota/buckets', '/api/quota/buckets/<string:bucket>')
api.add_resource(QuotaAllocations, '/api/quota/allocations', '/api/quota/allocations/<string:bucket>')
api.add_resource(QuotaUsers, '/api/quota/users/<string:user>')

if __name__ == '__main__':
    logging.basicConfig()
    app.run(debug=True, port=8888)
