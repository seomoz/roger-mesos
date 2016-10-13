import yaml

def parse_permissions_file(filename):
    with open(filename, 'r') as data_file:
        return yaml.load(data_file)
    return ''

def get_merged_data(user, allowed_users, allowed_actions, data, action):
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
        get_merged_data(u, allowed_users, allowed_actions, data, action)

def getAllowedNamespacePatterns(act_as, permissions):
    allowed_users_list = []
    get_merged_data(act_as, allowed_users_list, [], permissions, '')

    allowed_namespace_patterns = []

    for user in allowed_users_list:
        if 'allowed_names' in permissions[user]:
            for pattern in permissions[user]['allowed_names']:
                if not pattern in allowed_namespace_patterns:
                    allowed_namespace_patterns.append(pattern)

    return allowed_namespace_patterns

def merge_dicts(dict1, dict2):
    ''' Merge dict2 into dict1 recursively, merging lists for the same keys, overriding with latter value for non-list values, and return updated dict1 '''
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        for k, v in dict2.iteritems():
            if k not in dict1:
                dict1[k] = v
            else:
                dict1[k] = merge_dicts(dict1[k], v) # recursively merge dicts
    elif isinstance(dict1, list) and isinstance(dict2, list):
        dict1 += dict2 # merge lists
    else:
        dict1 = dict2 # latter value overrides
    return dict1

def merge_dicts_with_override(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    Reference - http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
