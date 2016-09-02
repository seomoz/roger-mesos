from flask import Flask, jsonify, request, render_template, redirect
from flask_restful import abort, Api, Resource
from flask_login import login_user, logout_user, login_required
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
    if request.method == 'POST':
        username = request.form['user']
        actas = request.form['act_as']
        passw = request.form['pass']
        if username and actas and passw:
            if (FileAuthenticator().instance.authenticate(username, passw) and
                actas in FileAuthorizer().instance.get_canactas_list(username)):
                session_user = SessionUser.get([username, actas])
                if session_user:
                    login_user(session_user, remember=True)
                    return redirect(request.args.get('redirect') or request.args.get('next') or '/')

    return render_template('index.html', **locals())

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

api.add_resource(Users, '/api/users')
api.add_resource(Groups, '/api/groups')
api.add_resource(CanActAsUsers, '/api/users/<user>/can_act_as')

if __name__ == '__main__':
    app.run(debug=True)
