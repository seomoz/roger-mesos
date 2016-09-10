from flask import Flask, jsonify, request, render_template, redirect, make_response, flash
from flask_restful import abort, Api, Resource
from flask_login import login_user, logout_user, login_required, current_user
from webargs import fields
from webargs.flaskparser import use_args
import os
import json

from authenticators import FileAuthenticator
from authorizers import FileAuthorizer
from resources import Users, Groups, CanActAsUsers
from sessions import login_manager, SessionUser
import sessions

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
api = Api(app)
login_manager.init_app(app)

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
    actas = request.cookies.get("actas") # try to get it from cookie
    if not actas:
        actas = request.headers.get("act_as_user") # try to get from header
    if not actas:
        actas = user # default to the user

    resource = request.headers.get('URI','')
    data = request.get_data()
    content_type = request.headers.get('content-type', '')
    action = request.headers.get('method', '')

    client_ip = request.headers.get('X-Forwarded-For')
    info = { 'clientip': str(client_ip), 'user': str(user), 'act_as': str(actas) }

    if not FileAuthorizer().instance.authorize(user, actas, resource, app.logger, info, data, content_type, action):
        abort(403)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/filter')
@login_required
def filter_response():
    '''
    This method filters the response (body) based on the access the current user has.
    Should typically be called by the proxy (internal) and not from outside.
    '''
    user = current_user.get_username()
    actas = request.cookies.get("actas") # try to get it from cookie
    if not actas:
        actas = request.headers.get("act_as_user") # try to get from header
    if not actas:
        actas = user # default to the user

    resource = request.headers.get('URI','')
    data = request.get_data()

    response = Authorizer().instance.filter_response(resource, data, actas)
    return Response(response=response, status=200, mimetype="application/json")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        passw = request.form.get('pass')
        actas = None
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
                    return make_response(render_template('index.html'))
            else:
                flash('Authentication failed.')
                return make_response(render_template('index.html'))
        else:
            actas = request.form.get('act_as')

        if not actas: # try to get from request cookie
            actas = request.cookies.get("actas")
        if not actas: # try to get from header
            actas = request.headers.get("act_as_user")

        if current_user.is_authenticated:
            if actas in FileAuthorizer().instance.get_canactas_list(current_user.get_username()):
                # all's well, let's set cookie and redirect
                resp = make_response(redirect(request.args.get('redirect') or request.args.get('next') or '/'))
                resp.set_cookie('actas', actas)
                return resp
            else:
                if actas:
                    flash('Not authorized to act as {}.'.format(actas))
                resp = make_response(render_template('index.html'))
                resp.set_cookie('actas', '', expires=0)
                return resp
        else:
            flash('Authentication required.')
            return make_response(render_template('index.html'))

    if not current_user.is_authenticated:
        flash('Please log in.')
    return make_response(render_template('index.html'))

@app.route('/logout')
def logout():
    logout_user()
    resp = make_response(render_template('index.html'))
    resp.set_cookie('actas', '', expires=0)
    return resp

api.add_resource(Users, '/api/users')
api.add_resource(Groups, '/api/groups')
api.add_resource(CanActAsUsers, '/api/users/<user>/can_act_as')

if __name__ == '__main__':
    app.run(debug=True, port=8888)
