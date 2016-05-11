import utils

class FileAuthenticator:
    class __FileAuthenticator:
        def __init__(self, filename):
            self.filename = filename
            self.data = utils.parse_permissions_file(filename)

        def authenticate(self, username, password):
            # Needs to be implemented to authenticate via a server like LDAP, etc 
            return True

    instance = None
    def __init__(self, filename):
        if not FileAuthenticator.instance:
            FileAuthenticator.instance = FileAuthenticator.__FileAuthenticator(filename)
        else:
            FileAuthenticator.instance.filename = filename

