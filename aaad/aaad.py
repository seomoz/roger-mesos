import sys, os, signal, base64
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

Listen = ('localhost', 8888)

import threading
from SocketServer import ThreadingMixIn
from authenticators import FileAuthenticator
from authorizers import FileAuthorizer


class AuthHTTPServer(ThreadingMixIn, HTTPServer, ):
    pass

class AuthHandler(BaseHTTPRequestHandler):
    ctx = {}
    authenticator = None
    method_to_action = { "GET" : "view" , "POST" : "create" , "PUT" : "update" , "DELETE" : "delete" }

    # Return True if request is processed and response sent, otherwise False
    # Set ctx['user'] and ctx['pass'] for authentication
    def do_GET(self):

        ctx = self.ctx
        ctx['action'] = 'getting basic http authorization header'
        auth_header = self.headers.get('Authorization')
        resource = self.headers.get('URI')
        action = self.method_to_action[self.headers.get('method')]
 
        print self.headers

        # Carry out Basic Authentication
        if auth_header is None or not auth_header.lower().startswith('basic '):
            self.send_response(401)
            self.end_headers()
            return False
        # Extract username and password
        auth_decoded = base64.b64decode(auth_header[6:])
        user, password = auth_decoded.split(':', 2)
        ctx['user'] = user
        ctx['pass'] = password

        if self.headers.get('act_as_user') is not None:
            act_as_user = self.headers.get('act_as_user')
        else:
            act_as_user = user

        # Invoke the Authenticator
        if not self.authenticate_request(user, password):
            self.send_response(401)
            self.end_headers()
            return False
        # Invoke the Authorizer
        if not self.authorize_request(user, act_as_user, action, resource):
            self.send_response(403)
            self.end_headers()
            return False

        self.log_message(ctx['action'])  # Continue request processing

        self.send_response(200)
        self.end_headers()
        return True

    def authenticate_request(self, user, password):
        ctx = self.ctx
        try:
            if not FileAuthenticator(permissions_file).instance.authenticate(user, password):
                raise Exception("Authentication Failed")
        except:
            self.auth_failed(ctx)
            return False
        return True

    def authorize_request(self, user, act_as_user, action, path):
        
        ctx = self.ctx
        try:
            if not FileAuthorizer(permissions_file).instance.authorize_act_as_user(user, act_as_user):
                raise Exception("Authorization Failed: {} cannot act as {}".format(user, act_as_user))

            if not FileAuthorizer(permissions_file).instance.authorize(act_as_user, path, action):
                raise Exception("Authorization Failed")
        except:
            self.auth_failed(ctx)
            return False
        return True

    def auth_failed(self, ctx, errmsg=None):
        msg = 'Error while ' + ctx['action']
        if errmsg:
            msg += ': ' + errmsg

        ex, value, trace = sys.exc_info()

        if ex != None:
            msg += ": " + str(value)

        if ctx.get('url'):
            msg += ', server="%s"' % ctx['url']

        if ctx.get('user'):
            msg += ', login="%s"' % ctx['user']

        self.log_error(msg)
        self.send_response(403)
        self.end_headers()


    def get_params(self):
        return {}


    def log_message(self, format, *args):
        if len(self.client_address) > 0:
            addr = BaseHTTPRequestHandler.address_string(self)
        else:
            addr = "-"

        sys.stdout.write("%s - [%s] %s\n" % (addr,
                                                self.log_date_time_string(), format % args))


    def log_error(self, format, *args):
        self.log_message(format, *args)  # Verify username/password against LDAP server

def exit_handler(signal, frame):
    global Listen

    if isinstance(Listen, basestring):
        try:
            os.unlink(Listen)
        except:
            ex, value, trace = sys.exc_info()
            sys.stderr.write('Failed to remove socket "%s": %s\n' %
                             (Listen, str(value)))
    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) < 1:
         sys.exit("Usage: %s <permissions_file> " % sys.argv[0])
    if not os.path.exists(sys.argv[1]):
         sys.exit("Permissions file - %s does not exist" % sys.argv[1])
    permissions_file = sys.argv[1];
    server = AuthHTTPServer(Listen, AuthHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()
