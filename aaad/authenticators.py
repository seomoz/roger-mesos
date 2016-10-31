
import os

from passlib.apache import HtpasswdFile

htpasswd_files = os.environ['HTPASSWD_FILES']


class FileAuthenticator:
    class __FileAuthenticator:
        '''Takes a commas separated list of htpasswd file paths in the HTPASSWD_FILES environment variable.
        '''
        def __init__(self, filenames_spec):
            self.data = self._parse_htpasswd_files(filenames_spec)

        def _parse_htpasswd_files(self, filenames_spec):
            data = ""
            filenames = filenames_spec.split(',')
            for item in filenames:
                filename = item.strip()
                if filename:
                    with open(filename, 'r') as data_file:
                        data = data + data_file.read()
            return HtpasswdFile.from_string(data)

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
            FileAuthenticator.instance = FileAuthenticator.__FileAuthenticator(htpasswd_files)
        else:
            FileAuthenticator.instance.filenames = htpasswd_files
