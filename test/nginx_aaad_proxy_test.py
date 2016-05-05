#!/usr/bin/python

from __future__ import print_function
import socket
import json
import sys
import os
import requests
import base64
import time

def post_data(url, headers, payload):
    result = requests.post(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)

def get_data(url, headers, payload=''):
    result = requests.get(url,data=payload,headers=headers)
    return result.status_code

def put_data(url, headers, payload):
    result = requests.put(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)

def delete_data(url,headers,payload):
    result = requests.delete(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)

def test_proxy_unauthorized_user(environment):

    # Provide garbage username and password
    encoded = base64.b64encode(b'garbage:garbage')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    headers['URI'] = "/moz-content/"
    app_url = 'http://'+environment+':4080/marathon/v2/apps'
    with open(parent_dir+"/sample_data.json") as json_file:
         json_data = json.load(json_file)
    result_code = post_data(app_url,headers,json_data)
    assert(result_code == 401)
    print("Create Failed: Unauthorized User")

    # Read App
    result_code = get_data(app_url,headers)
    assert(result_code == 401)
    print("Read Failed: Unauthorized User")

    # Update App
    app_url = 'http://'+environment+':4080/marathon/v2/apps/test-app'
    with open(parent_dir+"/update.json") as json_file:
         json_data = json.load(json_file)
    result_code = put_data(app_url,headers,json_data)
    assert(result_code == 401)
    print("Update Failed: Unauthorized User")

    # Delete App
    app_url = 'http://'+environment+':4080/marathon/v2/apps/test-app'
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code == 401)
    print("Delete Failed: Unauthorized User\n")

def test_proxy_valid_user(environment):

    try:

        app_url = 'http://'+environment+':4080/marathon/v2/apps/'

        # Creating Authorization for header using Base64 encoding (username:password)
        encoded = base64.b64encode(b'admin:admin')
        encoded = "Basic " + encoded
        headers = { "Content-Type": "application/json", "Authorization" : encoded }

        # Create App
        with open(parent_dir+"/sample_data.json") as json_file:
             json_data = json.load(json_file)

        result_code = post_data(app_url,headers,json_data)
        assert(result_code == 201)
        print("Create Test: Pass")

        # Read App
        result_code = get_data(app_url,headers)
        assert(result_code == 200)
        print("Read Test:   Pass")

        # Sleep has been added as it takes time for the app to get created
        time.sleep(5)

        # Update App
        app_url = 'http://'+environment+':4080/marathon/v2/apps/test-app'
        with open(parent_dir+"/update.json") as json_file:
             json_data = json.load(json_file)
        result_code = put_data(app_url,headers,json_data)
        assert(result_code == 200)
        print("Update Test: Pass")

        # Delete App
        app_url = 'http://'+environment+':4080/marathon/v2/apps/test-app'
        result_code = delete_data(app_url,headers,json_data)
        assert(result_code == 200)
        print("Delete Test: Pass\n")

    except:
        print("\nTest Case Failed")

def main(args):

    if len(args) < 2:
        print("Please provide environment, then retry.\nExiting...")
        sys.exit(0)

    machine = args[(len(args)-1)]

    # Check if the environment is up and reachable
    port = 4080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((machine, port))
    sock.settimeout(1)

    if result == 0:
        sock.close()
    else:
        print ("\nEnvironment {}: Unreachable".format(machine))
        sock.close()

    print("Executing Valid User Test:\n")
    test_proxy_valid_user(machine)
    print("Executing Unauthorized User Test:\n")
    test_proxy_unauthorized_user(machine)

if __name__ == "__main__":
    parent_dir = os.path.abspath(os.path.join(
                 os.path.dirname(os.path.realpath(__file__)), os.pardir, "test"))
    main(sys.argv)
