#!/usr/bin/python

import json
import sys
import htpasswd
import os

def generate_http_basic_auth_file(permissions_file, output_file):
    if not permissions_file:
        return
    permissions = None
    with open(permissions_file) as data_file:
        permissions = json.load(data_file)
    if os.path.exists(output_file):
        os.remove(output_file)
    htpasswd_file = open(output_file, "w")
    htpasswd_file.close()
    with htpasswd.Basic(output_file) as htpasswd_file:
        for permission in permissions["users"]:
            username = permission["user"]
            password = permission["password"]
            print username
            print password
            htpasswd_file.add(username, password)

            
if __name__ == '__main__':
        if len(sys.argv) < 3:
         sys.exit("Usage: %s <permissions_file> <output_file>" % sys.argv[0])
        permissions_file = sys.argv[1]
        output_file = sys.argv[2]
        generate_http_basic_auth_file(permissions_file, output_file)
