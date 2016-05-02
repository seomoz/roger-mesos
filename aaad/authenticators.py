import utils

class FileAuthenticator:
    class __FileAuthenticator:
        def __init__(self, filename):
            self.filename = filename
            self.data = utils.parse_permissions_file(filename)

        def authenticate(self, username, password):
            if not username or not password:
                return False
            else:
                for user in self.data["users"]:
                    if username == user["user"] and password == user["password"]:
                        return True
            return False

    instance = None
    def __init__(self, filename):
        if not FileAuthenticator.instance:
            FileAuthenticator.instance = FileAuthenticator.__FileAuthenticator(filename)
        else:
            FileAuthenticator.instance.filename = filename

