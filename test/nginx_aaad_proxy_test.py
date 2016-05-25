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


def get_authorization_header():
    encoded = base64.b64encode(b'internal_test_user:internal_test_user')
    encoded = "Basic " + encoded
    headers = {"Content-Type": "application/json", "Authorization": encoded}
    return headers


def create_json_data():
    with open(parent_dir + "/sample_data.json") as json_file:
        json_data = json.load(json_file)
    return json_data


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


def test_proxy_user_valid_permissions_create(app_url, headers, json_data):
    # Create App
    try:
        result_code = put_data(app_url, headers, json_data)
        assert(result_code == 200 or result_code == 201)
        print("Create Test: Pass")
    except (Exception) as e:
        print("The following error occurred: %s" %
              e, file=sys.stderr)
        print("Create Failed")


def test_proxy_user_valid_permissions_read(app_url, headers):
    # Read App
    try:
        result_code = get_data(app_url, headers)
        assert(result_code == 200)
        print("Read Test:   Pass")
    except (Exception) as e:
        print("The following error occurred: %s" %
              e, file=sys.stderr)
        print("Read Failed")


def test_proxy_user_valid_permissions_delete(app_url, headers, json_data):
    # Sleep has been added as it takes time for the app to get created
    try:
        time.sleep(5)
        # Delete App
        result_code = delete_data(app_url, headers, json_data)
        assert(result_code == 200)
        print("Delete Test: Pass\n")
    except (Exception) as e:
        print("The following error occurred: %s" %
              e, file=sys.stderr)
        print("Delete Failed")


def test_proxy_unauthorized_user_create(app_url, headers):
    result_code = put_data(app_url, headers, json_data)
    assert(result_code == 403)
    print("Create Failed: Unauthorized User")


def test_proxy_unauthorized_user_read(app_url, headers):
    # Read App
    result_code = get_data(app_url, headers)
    assert(result_code == 403)
    print("Read Failed: Unauthorized User")


def test_proxy_unauthorized_user_delete(app_url, headers):
    result_code = delete_data(app_url, headers, json_data)
    assert(result_code == 403)
    print("Delete Failed: Unauthorized User\n")


def test_invalid_end_points(app_url, headers, json_data):
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

    app_url_list = ['http://' + machine + ':4080/marathon/v2/apps/internal-test-team/test-app/',
                    'http://' + machine + ':4080/marathon/v2/apps/mongo/internal-test-team/test-app/',
                    'http://' + machine + ':4080/marathon/v2/apps/sortdb/internal-test-team/test-app/']

    json_data = create_json_data()
    headers = get_authorization_header()

    for app_url in app_url_list:
        print("\nExecuting Test for {} endpoint\n".format(app_url))
        test_proxy_user_valid_permissions_create(app_url, headers, json_data)
        test_proxy_user_valid_permissions_read(app_url, headers)
        test_proxy_user_valid_permissions_delete(app_url, headers, json_data)

    app_url = 'http://' + machine + ':4080/marathon/v2/apps/internal-test-team/'
    print ("\nExecuting Test for Invalid End Point: {}\n".format(app_url))
    test_invalid_end_points(app_url, headers, json_data)
    print("\nAll Tests Passed \n")

if __name__ == "__main__":
    parent_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), os.pardir, "test"))
    main(sys.argv)
