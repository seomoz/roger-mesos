import utils
import re
import json
import yaml
import os
import sys
from validators import Validator
from frameworkUtils import FrameworkUtils
import logging

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

permissions_file = os.getenv('PERMISSIONS_FILE')

class AuthorizeResult:

    def __init__(self, result, messages=None):
        self.result = result
        self.messages = messages

    def __nonzero__(self):
        return self.result

class FileAuthorizer:
    class __FileAuthorizer:

        def __init__(self, filename):
            self.filename = filename
            self.data = self._parse_permissions_file(filename)

        def resource_check(self, request_uri, body, allowed_actions, content_type):
            for item in allowed_actions:
                uri = item.keys()
                pattern = uri[0]
                prog = re.compile("^{}$".format(pattern))
                result = prog.match(request_uri)
                if result:

                    if (item[pattern] == {}):
                        return True
                    else:
                        if body == "":
                            return False
                        else:
                            if content_type.lower() == "application/json" or content_type.lower() == "application/javascript":
                                try:
                                    template_data = json.loads(body)
                                except (Exception) as e:
                                    logger.error("Request body is an invalid json - {}".format(str(e)))
                                    return False

                                attribute_rules = item[pattern]
                                valid = self.validate_request_body(attribute_rules, template_data)
                                return valid
                            else:
                                return False

                        attribute_rules = item[pattern]
                        valid = self.validate_request_body(attribute_rules, template_data)
                        return valid

            return False

        def validate_request_body(self, attribute_rules, body):
            for attribute in attribute_rules.keys():
                items = attribute.split('/')
                temp_data = body
                for item in items:
                    if not type(temp_data) == dict:
                        return False
                    if item in temp_data.keys():
                        temp_data = temp_data[item]
                    else:
                        #Attribute not available in request body
                        return False

                prog = re.compile("^{}$".format(attribute_rules[attribute]))
                if type(temp_data) == list:
                    for item_val in temp_data:
                        result = prog.match(item_val)
                        if not result:
                            return False
                else:   # temp_data is of type 'str'
                    result = prog.match(temp_data)
                    if not result:
                        return False

            return True

        def _get_act_as_list(self, user):
            allowed_users_list = []
            if user in self.data.keys():
                self._get_merged_data(user, allowed_users_list, [], self.data, '')
            return allowed_users_list

        def authorize(self, user, act_as, resource, data, content_type, action = None):
            if not action:
                action = 'GET'
            if not user or not act_as or not resource:
                return AuthorizeResult(False)

            if user not in self.data.keys() or act_as not in self.data.keys():
                logger.warning("Invalid user [{}] or act as user [{}]".format(user, act_as))
                return AuthorizeResult(False)

            if user != act_as:
                if 'can_act_as' not in self.data[user]:
                    logger.warning("User {} not authorized to act as {}".format(user, act_as))
                    return AuthorizeResult(False)

            allowed_users_list = self._get_act_as_list(user)

            if act_as not in allowed_users_list:
                logger.warning("User {} not authorized to act as {}".format(user, act_as))
                return AuthorizeResult(False)

            allowed_users_list = []
            allowed_actions = []
            if 'action' in self.data[act_as] and self.data[act_as]['action'] != None:
                for item in self.data[act_as]['action'][action]:
                    temp_item = {}
                    if type(item) == str:
                        temp_item = {}
                        temp_item[item] = {}
                    else:
                        if type(item) == dict:
                            temp_item = item

                    if not temp_item in allowed_actions:
                        allowed_actions.append(temp_item)

            self._get_merged_data(act_as, allowed_users_list, allowed_actions, self.data, action)

            result = self.resource_check(resource, data, allowed_actions, content_type)
            if result == False:
                logger.warning("User {} acting as {} is not authorized to access [{}]".format(user, act_as, resource))
                return AuthorizeResult(False)

            try:
                validator = Validator()
                framework = FrameworkUtils().getFramework(resource)
                if not validator.validate(act_as, resource, action, data, framework):
                    logger.warning("Validation failed. Reasons - {}".format(validator.messages))
                    return AuthorizeResult(False, validator.messages)
            except (Exception) as e:
                logger.error("Failed in request validation - {}".format(str(e)))
                return AuthorizeResult(False)

            return AuthorizeResult(True)

        def get_user_list(self, type=None):
            if not type:
                return self.data.keys()
            users = []
            for key, data in self.data.items():
                if data.get('type', 'user') == type:
                    users.append(key)
            return users

        def get_canactas_list(self, user):
            actas_users = []
            for key in self._get_act_as_list(user):
                if (self.data.get(key).get('type', 'user') != 'internal'):
                    actas_users.append(key)
            return actas_users

        def is_user_valid(self, user):
            return user in self.data.keys()

        def filter_response(self, resource, data, actas):
            framework = FrameworkUtils().getFramework(resource)
            allowed_namespaces = self.get_allowed_namespace_patterns(actas)
            if not allowed_namespaces:    #Empty list
                return ""
            return framework.filterResponseBody(data, allowed_namespaces, resource)

        def _parse_permissions_file(self, filename):
            permissions = {}
            for item in filename.split(','):
                with open(item.strip(), 'r') as data_file:
                    utils.merge_dicts(permissions, yaml.load(data_file))
            return permissions

        def _get_merged_data(self, user, allowed_users, allowed_actions, data, action):
            if user in allowed_users:
                return
            allowed_users.append(user)
            if action != '' and 'action' in data[user]:
                if data[user]['action'] != None and action in data[user]['action']:
                    for item in data[user]['action'][action]:
                        temp_item = {}
                        if type(item) == str:
                            temp_item = {}
                            temp_item[item] = {}
                        else:
                            if type(item) == dict:
                                temp_item = item
                        if not temp_item in allowed_actions:
                            allowed_actions.append(temp_item)
            if 'can_act_as' not in data[user]:
                return
            for u in data[user]['can_act_as']:
                self._get_merged_data(u, allowed_users, allowed_actions, data, action)

        def get_allowed_namespace_patterns(self, act_as):
            if not self.is_user_valid(act_as):
                return []
            permissions = self.data
            allowed_users_list = []
            self._get_merged_data(act_as, allowed_users_list, [], permissions, '')
            allowed_namespace_patterns = []
            for user in allowed_users_list:
                if 'allowed_names' in permissions[user]:
                    for pattern in permissions[user]['allowed_names']:
                        if not pattern in allowed_namespace_patterns:
                            allowed_namespace_patterns.append(pattern)
            return allowed_namespace_patterns

    instance = None
    def __init__(self):
        if not FileAuthorizer.instance:
            FileAuthorizer.instance = FileAuthorizer.__FileAuthorizer(permissions_file)
        else:
            FileAuthorizer.instance.filename = permissions_file
