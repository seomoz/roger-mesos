import utils

class FileAuthorizer:
    class __Singleton:
        data = None

        def __init__(self, file):
            self.file = file
            self.data = utils.parse_permissions_file(file)

        def authorize_act_as_user(self, user, act_as_user):
            return True

        def authorize(self, username, resource, action = "view"):
            if not username or not resource:
                return False
            else:
                for user in self.data["users"]:
                    if username == user["user"]:
                        for permission in user["user"]["permissions"]:
                            if resource.startsWith(permission["on"]) and permission["allowed"] == action:
                                return True
            return False

    instance = None
    def __init__(self, file):
        if not FileAuthorizer.instance:
            FileAuthorizer.instance = FileAuthorizer.__Singleton(file)
        else:
            print "Singleton instance is already instantiated"
