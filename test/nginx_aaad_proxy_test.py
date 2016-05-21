#!/usr/bin/python
from __future__ import print_function
import socket
import json
import sys
import os
import requests
import base64
import time


def get_data(url, headers):
    result = requests.get(url, headers=headers, auth=('internal_test_user', 'internal_test_user'))
    return result.status_code


def put_data(url, headers, payload):
    result = requests.put(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)


def delete_data(url, headers, payload):
    result = requests.delete(url, data=json.dumps(payload), headers=headers, auth=('internal_test_user', 'internal_test_user'))
    return (result.status_code)


def test_proxy_common_user(environment):

    headers = {"Content-Type": "application/json"}
    # Test GET Access for common_access
    app_url = app_url = 'http://' + environment + ':4080/marathon/ui/'
    result_code = get_data(app_url, headers)
    assert(result_code == 200)
    print("GET Passed for marathon/ui/")

    app_url = app_url = 'http://' + environment + ':4080/marathon/public/api/'
    result_code = get_data(app_url, headers)
    assert(result_code == 200)
    print("GET Passed for marathon/public/api")

    app_url = app_url = 'http://' + environment + ':4080/marathon/v2/tasks/'
    result_code = get_data(app_url, headers)
    assert(result_code == 200)
    print("GET Passed for marathon/v2/tasks/\n")


def test_proxy_user_valid_permissions(environment):

    app_url = 'http://' + environment + ':4080/marathon/v2/apps/internal-test-team/test-app/'
    encoded = base64.b64encode(b'internal_test_user:internal_test_user')
    encoded = "Basic " + encoded
    headers = {"Content-Type": "application/json", "Authorization": encoded}

    # Create App
    with open(parent_dir + "/sample_data.json") as json_file:
        json_data = json.load(json_file)
    result_code = put_data(app_url, headers, json_data)
    assert(result_code == 200 or result_code == 201)
    print("Create Test: Pass")

    # Read App
    result_code = get_data(app_url, headers)
    assert(result_code == 200)
    print("Read Test:   Pass")
    # Sleep has been added as it takes time for the app to get created
    time.sleep(5)
    # Delete App
    result_code = delete_data(app_url, headers, json_data)
    assert(result_code == 200)
    print("Delete Test: Pass\n")

    app_url = 'http://' + environment + ':4080/marathon/v2/apps/mongo/internal-test-team/test-app/'

    # Create App
    with open(parent_dir + "/sample_data.json") as json_file:
        json_data = json.load(json_file)
    result_code = put_data(app_url, headers, json_data)
    assert(result_code == 200 or result_code == 201)
    print("Create Test: Pass for mongo end_point")

    # Read App
    result_code = get_data(app_url, headers)
    assert(result_code == 200)
    print("Read Test:   Pass for mongo end_point")
    # Sleep has been added as it takes time for the app to get created
    time.sleep(5)
    # Delete App
    result_code = delete_data(app_url, headers, json_data)
    assert(result_code == 200)
    print("Delete Test: Pass for mongo end_point\n")

    app_url = 'http://' + environment + ':4080/marathon/v2/apps/sortdb/internal-test-team/test-app/'

    # Create App
    with open(parent_dir + "/sample_data.json") as json_file:
        json_data = json.load(json_file)
    result_code = put_data(app_url, headers, json_data)
    assert(result_code == 200 or result_code == 201)
    print("Create Test: Pass for sortdb end_point")

    # Read App
    result_code = get_data(app_url, headers)
    assert(result_code == 200)
    print("Read Test:   Pass for sortdb end_point")
    # Sleep has been added as it takes time for the app to get created
    time.sleep(5)
    # Delete App
    result_code = delete_data(app_url, headers, json_data)
    assert(result_code == 200)
    print("Delete Test: Pass for sortdb end_point\n")


def test_proxy_unauthorized_user(environment):
    # Provide content username
    encoded = base64.b64encode(b'internal_test_user:internal_test_user')
    encoded = "Basic " + encoded
    headers = {"Content-Type": "application/json", "Authorization": encoded}

    # Create App
    app_url = 'http://' + environment + ':4080/marathon/v2/apps/moz-local/'
    with open(parent_dir + "/sample_data.json") as json_file:
        json_data = json.load(json_file)
    result_code = put_data(app_url, headers, json_data)
    assert(result_code == 403)
    print("Create Failed: Unauthorized User")

    # Read App
    result_code = get_data(app_url, headers)
    assert(result_code == 403)
    print("Read Failed: Unauthorized User")

    # Delete App
    app_url = 'http://' + environment + ':4080/marathon/v2/apps/moz-local/test-app'
    result_code = delete_data(app_url, headers, json_data)
    assert(result_code == 403)
    print("Delete Failed: Unauthorized User\n")


def test_invalid_end_points(environment):
    # Provide content username
    encoded = base64.b64encode(b'internal_test_user:internal_test_user')
    encoded = "Basic " + encoded
    headers = {"Content-Type": "application/json", "Authorization": encoded}

    # Create App
    app_url = 'http://' + environment + ':4080/marathon/v2/apps/internal-test-team/' # Invalid End Point
    with open(parent_dir + "/sample_data.json") as json_file:
        json_data = json.load(json_file)
    result_code = put_data(app_url, headers, json_data)
    assert(result_code == 403)
    print("Create Failed: Invalid End Point")


def main(args):

    if len(args) < 2:
        print("Please provide environment, then retry.\nExiting...")
        sys.exit(0)

    machine = args[(len(args) - 1)]

    # Check if the environment is up and reachable
    port = 4080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((machine, port))
    sock.settimeout(1)

    if result == 0:
        sock.close()
    else:
        print ("\nEnvironment {}: Unreachable. Exiting...".format(machine))
        sock.close()
        sys.exit(0)

    print("Executing common_access test:\n")
    test_proxy_common_user(machine)
    print("Executing Valid User Test:\n")
    test_proxy_user_valid_permissions(machine)
    print("Executing Unauthorized User Test:\n")
    test_proxy_unauthorized_user(machine)
    print("Executing Invalid End Point Test\n")
    test_invalid_end_points(machine)

    print("\nAll Tests Passed \n")

if __name__ == "__main__":
    parent_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), os.pardir, "test"))
    main(sys.argv)
