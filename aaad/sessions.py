from flask_login import LoginManager, UserMixin
from flask import Request
import ast
import os
from itsdangerous import URLSafeTimedSerializer
import base64

from authorizers import FileAuthorizer
from authenticators import FileAuthenticator

'''
References:
    * https://flask-login.readthedocs.io/en/latest/
    * http://thecircuitnerd.com/flask-login-tokens/
    * http://flask-security.readthedocs.io/en/latest/features.html
'''

# secret key used for the session user cookie
COOKIE_SECRET_KEY = os.environ['COOKIE_SECRET_KEY']
SESSION_TIMEOUT_SECONDS = int(os.getenv('SESSION_TIMEOUT_SECONDS', 120))

REMEMBER_COOKIE_DOMAIN = os.getenv('SESSION_ID_DOMAIN', None) # used by flask-login

login_manager = LoginManager()

'''
Note: With session_protection 'strong', this can fail in cases where this is
used as a stand in authenticator/authorizer called as a sub request from a proxy
This is because, the 'ip address' and 'user agent' are different.
For more details see - https://flask-login.readthedocs.io/en/latest/#session-protection
TODO: Update nginx configs to ensure client's ip and user agent are used in the sub request.
'''
login_manager.session_protection = 'basic'

#Login_serializer used to encryt and decrypt the cookie token for the remember me option of flask-login
login_serializer = URLSafeTimedSerializer(COOKIE_SECRET_KEY)

class SessionUser(UserMixin):
    actas = ''
    def __init__(self, username, userpasshash):
        ''' Note that the userpasshash can be some kind of a token too.'''
        self.user_id = username
        self.userpasshash = userpasshash

    def get_auth_token(self):
        ''' Encode a secure token for cookie. This is used to remember the user. '''
        return login_serializer.dumps(self.user_id, self.userpasshash)

    def get_id(self):
        return self.user_id

    def get_username(self):
        return self.user_id

    @staticmethod
    def get(user_id):
        '''
        Static method do determine if user_id is valid.
        Returns a SessionUser object if valid and None if not (as required be Flask-Login).
        '''
        if FileAuthorizer().instance.is_user_valid(user_id):
            userpasshash = FileAuthenticator().instance.get_hash(user_id)
            if userpasshash:
                return SessionUser(user_id, userpasshash)
        return None

@login_manager.user_loader
def load_user(user_id):
    '''
    This callback is used to reload the user object from the user ID stored in the session.
    It should take the unicode ID of a user, and return the corresponding user object.
    '''
    return SessionUser.get(user_id)

@login_manager.token_loader
def load_token(token):
    '''
    Flask-Login token_loader callback.
    The token_loader function asks this function to take the token that was
    stored on the users computer process it to check if its valid and then
    return a User Object if its valid or None if its not valid.
    '''
    #The Token itself was generated by User.get_auth_token (see above).
    #Decrypt the Security Token, data = [username, hashpass]
    data = login_serializer.loads(token, max_age=SESSION_TIMEOUT_SECONDS)
    #Find the User
    user = SessionUser.get(data[0])
    #Check userpasshash and return user or None
    if user and data[1] == user.userpasshash:
        return user
    return None

@login_manager.request_loader
def load_user_from_request(request):
    '''
    This callback is to support authentication using the Authorization header (basic auth)
    '''
    session_user = None
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_decoded = base64.b64decode(auth_header[6:]) #len('Basic ') = 6
        user, passw = auth_decoded.split(':', 2)
        if (FileAuthenticator().instance.authenticate(user, passw)):
            session_user = SessionUser.get(user)
        return session_user

    # finally, return None if this did not login the user
    return None
