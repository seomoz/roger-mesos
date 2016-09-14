from passlib.apache import HtpasswdFile
import os

htpasswd_file = os.environ['HTPASSWD_FILE']

class FileAuthenticator:
    class __FileAuthenticator:
        def __init__(self, filename):
            self.filename = filename
            self.data = HtpasswdFile(self.filename)

        def authenticate(self, username, password):
            """ Returns True if username exists and password is valid, False otherwise """
            if self.data.check_password(username, password):
                # Note: check_password returns None if username does not exists
                return True
            return False

        def get_hash(self, username):
            """ Returns a hash if username exists, None otherwise """
            return self.data.get_hash(username)

        def find_user(self, username):
            """ Returns True if usename exists in db, False otherwise """
            return username in self.data.users()

    instance = None
    def __init__(self):
        if not FileAuthenticator.instance:
            FileAuthenticator.instance = FileAuthenticator.__FileAuthenticator(htpasswd_file)
        else:
            FileAuthenticator.instance.filename = htpasswd_file
