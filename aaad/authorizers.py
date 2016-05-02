import utils

class FileAuthorizer:
    class __FileAuthorizer:

        def __init__(self, filename):
            self.filename = filename
            self.data = utils.parse_permissions_file(filename)

        #This needs to be implemented after the permissions file is updated.
        def authorize_act_as_user(self, user, act_as_user):
            return True

        def authorize(self, username, resource, action = "view"):
            if not username or not resource:
                return False
            else:
                for user in self.data["users"]:
                    if username == user["user"]:
                        for permission in user["permissions"]:
                            if resource.startswith(permission["on"]) and permission["allowed"] == action:
                                return True
            return False

    instance = None
    def __init__(self, filename):
        if not FileAuthorizer.instance:
            FileAuthorizer.instance = FileAuthorizer.__FileAuthorizer(filename)
        else:
            FileAuthorizer.instance.filename = filename

