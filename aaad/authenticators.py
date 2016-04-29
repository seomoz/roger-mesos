import utils

# todo: needs a lot of improvement File name should not have to be passed on
# todo: every call, make it configurable at the start for both classes
class FileAuthenticator:
    class __Singleton:
        data = None
        def __init__(self, file):
            self.file = file
            self.data = utils.parse_permissions_file(file)

        def authenticate(self, username, password):
            if not username or not password:
                return False
            else:
                for user in self.data["users"]:
                    if username == user["user"] and password == user["password"]:
                        return True
            return False
    instance = None
    def __init__(self, file):
        if not FileAuthenticator.instance:
            FileAuthenticator.instance = FileAuthenticator.__Singleton(file)
        else:
            print "Singleton instance is already instantiated"
