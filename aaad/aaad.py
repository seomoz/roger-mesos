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

    # Return True if request is processed and response sent, otherwise False
    # Set ctx['user'] and ctx['pass'] for authentication
    def do_GET(self):
        
        ctx = self.ctx
        ctx['action'] = 'getting basic http authorization header'
        auth_header = self.headers.get('Authorization')

        # This is just to get end to end working, need a lot of work here.
        print "**************************************************"
        print self.headers
        print "**************************************************"
        self.send_response(200)
        self.end_headers()
        return # for now just ensure that the request is coming here. nothing else
        if auth_header is None or not auth_header.lower().startswith('basic '):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm=' + ctx['realm'])
            self.end_headers()
            return True
        ctx['action'] = 'decoding credentials'

        try:
            auth_decoded = base64.b64decode(auth_header[6:])
            #auth_decoded = auth_header[6:]
            user, passwd = auth_decoded.split(':', 2)
            ctx['user'] = user
            ctx['pass'] = passwd

            if not FileAuthenticator(permissions_file).instance.authenticate(user, passwd):
                raise Exception("Authentication Failed")
            if not FileAuthorizer(permissions_file).instance.authorize(user, self.path, "view"):
                raise Exception("Authorization Failed")
        except:
            self.auth_failed(ctx)
            return True

        self.log_message(ctx['action'])  # Continue request processing
        return False  # Log the error and complete the request with appropriate status


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
    # this is a very dirty way to initialize but will change it later
    # for now we disabled the permission files check for authorization
#     if len(sys.argv) < 1:
#         sys.exit("Usage: %s <permissions_file> " % sys.argv[0])

#     if not os.path.exists(sys.argv[1]):
#         sys.exit("Permissions file - %s does not exist" % sys.argv[1])
#     global permissions_file
#     permissions_file = sys.argv[1];
    server = AuthHTTPServer(Listen, AuthHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()





