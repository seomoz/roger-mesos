import yaml

def parse_permissions_file(filename):
    with open(filename, 'r') as data_file:
        return yaml.load(data_file)
    return ''

