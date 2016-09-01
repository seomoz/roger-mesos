from flask import Flask, jsonify, request, render_template
from flask_restful import reqparse, abort, Api, Resource
from webargs import fields
from webargs.flaskparser import use_args
import os
import json

from authorizers import FileAuthorizer

app = Flask(__name__)
api = Api(app)

permissions_file = os.getenv('PERMISSIONS_FILE')

@app.route('/')
def authenticate():
    # authenticate
    abort(401)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        do_the_login()
    else:
        # show the login page
        file_authorizer = FileAuthorizer(permissions_file).instance
        user_list = file_authorizer.get_user_list('user')
        return render_template('index.html', **locals())

def do_the_login():
    abort(403)

class Users(Resource):
    get_args = {
        'startswith': fields.Str(required=False)
    }
    @use_args(get_args)
    def get(self, args):
        file_authorizer = FileAuthorizer(permissions_file).instance
        users = file_authorizer.get_user_list('user')
        startswith = args.get('startswith')
        if not startswith:
            return jsonify(users)
        filtered_users = []
        for user in users:
            if user.startswith(startswith):
                filtered_users.append(user)
        return jsonify(filtered_users)

class Groups(Resource):
    def get(self):
        file_authorizer = FileAuthorizer(permissions_file).instance
        groups = file_authorizer.get_user_list('group')
        return jsonify(groups)

class CanActAsUsers(Resource):
    def get(self, user):
        file_authorizer = FileAuthorizer(permissions_file).instance
        actas_users = file_authorizer.get_canactas_list(user)
        return jsonify(actas_users)

api.add_resource(Users, '/api/users')
api.add_resource(Groups, '/api/groups')
api.add_resource(CanActAsUsers, '/api/users/<user>/can_act_as')

if __name__ == '__main__':
    app.run(debug=True)
