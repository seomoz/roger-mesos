import sys, os, signal, base64
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

Listen = ('localhost', 8888)

import threading
import logging
import argparse
import utils
from SocketServer import ThreadingMixIn
from authenticators import FileAuthenticator
from authorizers import FileAuthorizer
from frameworkUtils import FrameworkUtils
import cgi
import urlparse
from datetime import datetime
import crypt_utils
from Cookie import SimpleCookie

session_timeout_seconds = int(os.getenv('SESSION_TIMEOUT_SECONDS', 120))
secret_key = os.getenv('SECRET_KEY', 'test_key_NOT_a_secret')
session_id_key = os.getenv('SESSION_ID_KEY', 'aaadsid')
htpasswd_file = os.getenv('HTPASSWD_FILE', '')

class AuthHTTPServer(ThreadingMixIn, HTTPServer, ):
    pass

class AuthHandler(BaseHTTPRequestHandler):
    ctx = {}
    authenticator = None
    frameworkUtils = FrameworkUtils()

    def do_GET(self):

        ctx = self.ctx
        ctx['action'] = 'getting basic http authorization header'
        auth_header = self.headers.get('Authorization')
        resource = self.headers.get('URI')
        action = self.headers.get('method')
        client_ip = self.headers.get('X-Forwarded-For')
        auth_action = self.headers.get("auth_action", "")

        self.info = { 'clientip': str(client_ip) }

        user = None
        password = None
        act_as_user = None
        sid = None

        # Read the seesion id cookie if available
        cookie_str = self.headers.get('Cookie')
        if cookie_str:
            cookie_obj = SimpleCookie(cookie_str)
            sid_morsel = cookie_obj.get(session_id_key, None)
            if sid_morsel is not None:
                sid = sid_morsel.value
                if sid == '0':
                    sid = None

        if sid: # If session_id_key cookie exists use that
            decoded = self.decode_sessionid(sid)
            if not decoded:
                self.send_response(401)
                self.send_header('Set-Cookie', '{}=0'.format(session_id_key)) # remove session id cookie
                self.end_headers()
                return
            user = decoded['user']
            password = decoded['password']
            act_as_user = decoded['act_as_user']
        else: # Else attempt Basic Authentication
            if auth_header is None or not auth_header.lower().strip().startswith('basic '):
                self.send_response(401)
                self.send_header('Set-Cookie', '{}=0'.format(session_id_key)) # remove session id cookie
                self.end_headers()
                return
            auth_decoded = base64.b64decode(auth_header[6:])
            user, password = auth_decoded.split(':', 2)
            if self.headers.get('act-as-user'):
                act_as_user = self.headers.get('act-as-user')
            else:
                act_as_user = user

        ctx['user'] = user
        ctx['pass'] = password
        self.info.update({ 'user': str(user), 'act_as': str(act_as_user) })
        logger.debug("\n{}".format(self.headers), extra = self.info)
        if action.lower() in [ "get", "head", "connect", "trace" ]:
            logger.info("{} {}".format(action, resource), extra = self.info)
        else:
            logger.warning("{} {}".format(action, resource), extra = self.info)

        content_len = int(self.headers.getheader('content-length', 0))
        body = self.rfile.read(content_len)
        logger.debug("\n{}".format(body), extra = self.info)

        content_type = self.headers.getheader("content-type", "")

        if auth_action == "filter_response":
            filtered_response = self.filter_response(body, resource, act_as_user, permissions)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(filtered_response)
            self.wfile.close()
            return

        if not self.authenticate_request(user, password):
            self.send_response(401)
            self.send_header('Set-Cookie', '{}=0'.format(session_id_key)) # remove session id cookie
            self.end_headers()
            return

        if not self.authorize_request(user, act_as_user, action, resource, body, content_type):
            self.send_response(403)
            self.send_header('Set-Cookie', '{}=0'.format(session_id_key)) # remove session id cookie
            self.end_headers()
            return

        self.log_message(ctx['action'])  # Continue request processing
        self.send_response(200)
        if not sid: # if sid was absent, let's add a sid
            self.send_header('Set-Cookie', '{}={}'.format(session_id_key, self.encode_sessionid(user, password, act_as_user)))
        self.end_headers()
        return

    def do_POST(self):
        """
            Adds a session id cookie for a valid user/pass/actas combination.
            This method adds a Set-Cookie header (from the form data) of the format:
                'user|pass|actas|validity'
            After doing this it responds with a 302 to the 'redirect' data in the form
            or a 200 if no 'redirect' data exists.
        """
        ctx = self.ctx
        ctx['action'] = 'creating new session'
        resource = self.headers.get('URI')
        action = self.headers.get('method')
        client_ip = self.headers.get('X-Forwarded-For')

        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        user = postvars.get('user', '')[0]
        password = postvars.get('pass', '')[0]
        act_as_user = postvars.get('act_as', '')[0]
        if not act_as_user:
            act_as_user = user
        redirect = postvars.get('redirect', '')[0]
        self.info = {'clientip': str(client_ip), 'user': str(user), 'act_as': str(act_as_user), 'redirect': str(redirect)}

        if(redirect):
            self.send_response(302)
            self.send_header('Location', redirect)
        else:
            self.send_response(200)

        message = ''
        file_authorizer = FileAuthorizer(permissions_file).instance
        if self.authenticate_request(user, password) and act_as_user in file_authorizer.get_act_as_list(user):
            # create and set a session id cookie
            self.send_header('Set-Cookie', '{}={}'.format(session_id_key, self.encode_sessionid(user, password, act_as_user)))
            message = 'Authenticated.'
        else:
            self.send_header('Set-Cookie', '{}=0'.format(session_id_key)) # remove session id cookie
            message = 'Authentication Failed.'

        self.end_headers()
        self.wfile.write(message)
        return

    def encode_sessionid(self, user, passw, actas):
        sessionid = crypt_utils.encode(secret_key, '{}|{}|{}|{}'.format(user, passw, actas, self.get_now_in_seconds() + session_timeout_seconds))
        return sessionid

    def decode_sessionid(self, sessionid):
        decoded = crypt_utils.decode(secret_key, sessionid)
        [ user, password, actas, valid_until_s ] = decoded.split('|')
        if not ( user or password or actas or valid_until_s ):
            return None
        valid_until = 0
        try:
            valid_until = float(valid_until_s)
        except:
            return None
        if self.get_now_in_seconds() > valid_until:
            return None
        return { 'user': user, 'password': password, 'act_as_user': actas }

    def get_now_in_seconds(self):
        return (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()

    def filter_response(self, body, resource, act_as_user, permissions):
        framework = self.frameworkUtils.getFramework(resource)
        allowed_namespaces = utils.getAllowedNamespacePatterns(act_as_user, permissions)

        if not allowed_namespaces:    #Empty list
            return ""

        response = framework.filterResponseBody(body, allowed_namespaces, resource)
        return response

    def authenticate_request(self, user, password):
        ctx = self.ctx
        try:
            if not FileAuthenticator(htpasswd_file).instance.authenticate(user, password):
                return False
        except:
            self.auth_failed(ctx)
            return False

        return True

    def authorize_request(self, user, act_as_user, action, path, data, content_type):
        ctx = self.ctx
        file_authorizer = FileAuthorizer(permissions_file).instance
        try:
            if not file_authorizer.authorize(user, act_as_user, path, logging, self.info, data, content_type, action):
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
        return

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
    permissions = utils.parse_permissions_file(permissions_file)
    server = AuthHTTPServer(Listen, AuthHandler)
    signal.signal(signal.SIGINT, exit_handler)
    server.serve_forever()
