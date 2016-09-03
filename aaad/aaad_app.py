from flask import Flask, jsonify, request, render_template, redirect, make_response, flash
from flask_restful import abort, Api, Resource
from flask_login import login_user, logout_user, login_required, current_user
from webargs import fields
from webargs.flaskparser import use_args
import os

from authenticators import FileAuthenticator
from authorizers import FileAuthorizer
from resources import Users, Groups, CanActAsUsers
from sessions import login_manager, SessionUser
import sessions

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
api = Api(app)
login_manager.init_app(app)

@app.route('/')
@login_required
def default():
    # authenticate
    return render_template('index.html')

@app.route('/marathon')
@login_required
def marathon():
    # authenticate
    return render_template('index.html')

@app.route('/chronos')
@login_required
def chronos():
    # authenticate
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    resp = make_response(render_template('index.html'))
    if request.method == 'POST':
        resp = redirect(request.args.get('redirect') or request.args.get('next') or '/')
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
                flash('Authentication failed.')
        else:
            actas = request.form.get('act_as')

        if not actas: # try to get from request cookie
            actas = request.cookies.get("actas")
        if not actas: # try to get from header
            actas = request.headers.get("act_as_user")
        elif current_user.is_authenticated:
            if actas in FileAuthorizer().instance.get_canactas_list(current_user.get_username()):
                resp.set_cookie('actas', actas)
            else:
                resp.set_cookie('actas', '', expires=0)
                flash('{} is not authorized to act as {}.'.format(current_user.get_username(), actas))

    return resp

@app.route('/logout')
def logout():
    logout_user()
    resp = make_response(render_template('index.html'))
    resp.set_cookie('actas', '', expires=0)
    return resp

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

api.add_resource(Users, '/api/users')
api.add_resource(Groups, '/api/groups')
api.add_resource(CanActAsUsers, '/api/users/<user>/can_act_as')

if __name__ == '__main__':
    app.run(debug=True)
