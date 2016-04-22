import utils

class FileAuthorizer:
    class __Singleton:
        data = None
        def __init__(self, file):
            self.file = file
            self.data = utils.parse_permissions_file(file)

        def authorize(self, username, resource, action = "view"):
            if not username or not resource:
                return False
            else:
                for user in self.data["users"]:
                    if username == user["user"]:
                        for permission in user["user"]["permissions"]:
                            if resource.startsWith(permission["path"]) and permission["allowed"] == action:
                                return True
            return False
