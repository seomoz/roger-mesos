import utils
import re
import json
import os
import sys

class FileAuthorizer:
    class __FileAuthorizer:

        def __init__(self, filename):
            self.filename = filename
            self.data = utils.parse_permissions_file(filename)

        def get_merged_data(self, user, allowed_users, allowed_actions, data, action):
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
                self.get_merged_data(u, allowed_users, allowed_actions, data, action)

        def resource_check(self, request_uri, data, allowed_actions):
            for item in allowed_actions:
                uri = item.keys()
                pattern = uri[0]
                prog = re.compile("^{}$".format(pattern))
                result = prog.match(request_uri)
                if result:
                    if data != "":
                        try:
                            template_data = json.loads(data)
                        except (Exception) as e:
                            logger.warning("Request body is an invalid json")
                            return False

                        attribute_rules = item[pattern]
                        valid = self.validate_request_body(attribute_rules, template_data)
                        return valid
                    else:
                        return (item[pattern] == {})

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
                result = prog.match(temp_data)
                if result:
                    continue
                else:
                    return False

            return True

        def authorize(self, user, act_as, resource, logging, info, data, action = "GET"):
            logger = logging.getLogger("Authorization")
            if not user or not act_as or not resource:
                return False

            if user not in self.data.keys() or act_as not in self.data.keys():
                logger.warning("Invalid user", extra = info)
                return False            

            if user != act_as:
                if 'can_act_as' not in self.data[user]:
                    logger.warning("User act as failed", extra = info)
                    return False

            allowed_users_list = []
            self.get_merged_data(user, allowed_users_list, [], self.data, '')

            if act_as not in allowed_users_list:
                logger.warning("User act as failed", extra = info)
                return False

            allowed_users_list = []
            allowed_actions = []
            if 'action' in self.data[act_as] and self.data[act_as]['action'] != None:
                for item in self.data[user]['action'][action]:
                    temp_item = {}
                    if type(item) == str:
                        temp_item = {}
                        temp_item[item] = {}
                    else:
                        if type(item) == dict:
                            temp_item = item

                    if not temp_item in allowed_actions:
                        allowed_actions.append(temp_item)

            self.get_merged_data(act_as, allowed_users_list, allowed_actions, self.data, action)
         
            result = self.resource_check(resource, data, allowed_actions)
            if result == False:
                logger.warning("Unauthorized [{}]".format(resource), extra = info)
                return False

            return True

    instance = None
    def __init__(self, filename):
        if not FileAuthorizer.instance:
            FileAuthorizer.instance = FileAuthorizer.__FileAuthorizer(filename)
        else:
            FileAuthorizer.instance.filename = filename

