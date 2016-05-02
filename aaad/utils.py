import json

def parse_permissions_file(filename):
    with open(filename, 'r') as data_file:
        return json.load(data_file)
    return ''

