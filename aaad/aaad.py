import sys, os, signal, base64
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

Listen = ('localhost', 8888)

import threading
import logging
import argparse
from SocketServer import ThreadingMixIn
from authenticators import FileAuthenticator
from authorizers import FileAuthorizer


class AuthHTTPServer(ThreadingMixIn, HTTPServer, ):
    pass

class AuthHandler(BaseHTTPRequestHandler):
    ctx = {}
    authenticator = None

    def do_GET(self):

        ctx = self.ctx
        ctx['action'] = 'getting basic http authorization header'
        auth_header = self.headers.get('Authorization')
        resource = self.headers.get('URI')
        action = self.headers.get('method')
        client_ip = self.headers.get('X-Forwarded-For')

        # Carry out Basic Authentication
        if auth_header is None or not auth_header.lower().strip().startswith('basic '):
            self.send_response(401)
            self.end_headers()
            return False

        auth_decoded = base64.b64decode(auth_header[6:])
        user, password = auth_decoded.split(':', 2)
        ctx['user'] = user
        ctx['pass'] = password

        if self.headers.get('act-as-user'):
            act_as_user = self.headers.get('act-as-user')
        else:
            act_as_user = user

        info = {'clientip': str(client_ip), 'user': str(user), 'act_as': str(act_as_user)}
        self.info = info
        logger.debug("\n{}".format(self.headers), extra = info)
        logger.info("{} {}".format(action, resource), extra = info)

        if not self.authenticate_request(user, password):
            self.send_response(401)
            self.end_headers()
            return False

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
                return False
        except:
            self.auth_failed(ctx)
            return False

        return True

    def authorize_request(self, user, act_as_user, action, path):
        ctx = self.ctx
        file_authorizer = FileAuthorizer(permissions_file).instance
        try:
            if not file_authorizer.authorize(user, act_as_user, path, logging, self.info, action):
                return False

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

    def log_message(self, format, *args):
        logger.debug("{}".format(args), extra = self.info)

    def log_error(self, format, *args):
        self.log_message(format, *args)

def exit_handler(signal, frame):
    global Listen

    if isinstance(Listen, basestring):
        try:
            os.unlink(Listen)
        except:
            ex, value, trace = sys.exc_info()
            logger.error('Failed to remove socket "%s": %s\n' %
                             (Listen, str(value)))
    sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(prog='AAAd Daemon', description="Audits every request, " \
                 "authenticates user and checks if user is authorized")
    parser.add_argument('perm_file', metavar='perm_file', help="Permissions file")
    parser.add_argument('-l', '--log-level', metavar='log_level', help="Log Level. Example: 'debug' or 'info'")
    return parser

if __name__ == '__main__':

    log_levels = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

    parser = parse_args()
    args = parser.parse_args()
    permissions_file = args.perm_file
    if not os.path.exists(permissions_file):
        sys.exit("Permissions file - {} does not exist".format(permissions_file))
    log_level = "warning"
    if args.log_level:
        log_level = args.log_level.lower()
    if log_level not in log_levels.keys():
         sys.exit("LOG LEVEL is not valid. Allowed levels {}.".format(log_levels.keys()))
    level = log_levels.get(log_level, logging.NOTSET)
    FORMAT = "[%(asctime)-15s] %(levelname)s - %(name)s - IP:%(clientip)s User:%(user)s ActAs:%(act_as)s - %(message)s"
    logging.basicConfig(level=level, format=FORMAT)
    logger = logging.getLogger("AAAd")
    server = AuthHTTPServer(Listen, AuthHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()
