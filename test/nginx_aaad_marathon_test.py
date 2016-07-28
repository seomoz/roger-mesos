#!/usr/bin/python
from __future__ import print_function
import socket
import json
import sys
import os
import requests
import base64
import time
from testutils import TestUtils


def main(args):

    if len(args) < 2:
        print("Please provide environment, then retry.\nExiting...")
        sys.exit(0)

    utilsObj = TestUtils()
    marathon_url = args[(len(args) - 1)]

    app_url_list = [marathon_url + '/v2/apps/internal-test-team/test-app/',
                    marathon_url + '/v2/apps/db1/internal-test-team/test-app/',
                    marathon_url + '/v2/apps/db2/internal-test-team/test-app/']

    json_data = utilsObj.create_json_data("/sample_data.json")
    headers = utilsObj.get_authorization_header()

    for app_url in app_url_list:
        print("\nExecuting Test for {} endpoint\n".format(app_url))
        utilsObj.test_proxy_user_valid_permissions_create(app_url, headers, json_data)
        utilsObj.test_proxy_user_valid_permissions_read(app_url, headers)
        utilsObj.test_proxy_user_valid_permissions_delete(app_url, headers, json_data)

    json_data = utilsObj.create_json_data("/sample_data.json")
    app_url = marathon_url + '/v2/apps/internal-test-team/'
    print ("\nExecuting Test for Invalid End Point: {}\n".format(app_url))
    utilsObj.test_invalid_end_points(app_url, headers, json_data)

    json_data = ""
    print ("\nExecuting PUT With Non JSON Body:\n")
    app_url = marathon_url + '/v2/apps/internal-test-team/'
    utilsObj.test_proxy_user_valid_permissions_create(app_url, headers, json_data)

    print ("\nExecuting PUT Without Body:\n")
    app_url = marathon_url + '/v2/apps/internal-test-team/'
    utilsObj.test_proxy_user_valid_permissions_create_no_body(app_url, headers)

    print("\nAll Tests Passed \n")

if __name__ == "__main__":
    main(sys.argv)
