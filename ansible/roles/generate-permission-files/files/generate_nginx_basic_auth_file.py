#!/usr/bin/python

from __future__ import print_function
import json
import sys
import htpasswd
import yaml
import os

def generate_http_basic_auth_file(permissions_file, output_file):
    if not permissions_file:
        return
    permissions = ""
    with open(permissions_file) as data_file:
        permissions = yaml.load(data_file)

    if os.path.exists(output_file):
        os.remove(output_file)
    htpasswd_file = open(output_file, "w")
    with htpasswd.Basic(output_file) as htpasswd_file:
        for username in permissions.keys():
            if not username.endswith("_team"):
                htpasswd_file.add(username, username)
            
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("Usage: %s <permissions_file> <output_file>" % sys.argv[0])
    permissions_file = sys.argv[1]
    output_file = sys.argv[2]
    generate_http_basic_auth_file(permissions_file, output_file)
