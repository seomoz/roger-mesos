#!/usr/bin/python

from __future__ import print_function
import json
import sys
import htpasswd
import yaml
import os

def generate_nginx_basic_auth_file(permissions_files, output_file):
    if not permissions_files:
        return

    permissions = {}
    for item in permissions_files.split(','):
        filename = item.strip()
        if filename:
            with open(filename) as data_file:
                permissions = merge_dicts(permissions, yaml.load(data_file))

    if os.path.exists(output_file):
        os.remove(output_file)
    htpasswd_file = open(output_file, "w")
    with htpasswd.Basic(output_file) as htpasswd_file:
        for username in permissions.keys():
            user_data = permissions[username]
            type = user_data.get('type', 'user')
            if type == "user":
                htpasswd_file.add(username, username)

def merge_dicts(dict1, dict2):
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        for k, v in dict2.iteritems():
            dict1[k] = v

    return dict1
            
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("Usage: %s <permission_files_delimited_by_comma> <output_file>" % sys.argv[0])
    permissions_files = sys.argv[1]
    output_file = sys.argv[2]
    generate_nginx_basic_auth_file(permissions_files, output_file)
