#!/usr/bin/python
from __future__ import print_function
import json
import sys
import os
import requests
import base64
import time


class TestUtils:

    def get_data(self, url, headers):
        result = requests.get(url, auth=('internal_test_user', 'internal_test_user'))
        return result.status_code

    def put_data(self, url, headers, payload):
        result = requests.put(url, data=json.dumps(payload), headers=headers)
        return (result.status_code)

    def delete_data(self, url, headers, payload):
        result = requests.delete(url, data=json.dumps(payload), auth=('internal_test_user', 'internal_test_user'))
        return (result.status_code)

    def get_authorization_header(self):
        encoded = base64.b64encode(b'internal_test_user:internal_test_user')
        encoded = "Basic " + encoded
        headers = {"Content-Type": "application/json", "Authorization": encoded}
        return headers

    def create_json_data(self, file_path):
        parent_dir = os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), os.pardir, "test"))
        with open(parent_dir + file_path) as json_file:
            json_data = json.load(json_file)
        return json_data

    def test_proxy_user_invalid_body(self, app_url, headers, json_data):
        # Create App
        try:
            result_code = self.put_data(app_url, headers, json_data)
            assert(result_code == 403)
            print("Invalid Body Test: Pass")
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
            print("Invalid Body Test Failed")

    def test_proxy_user_valid_permissions_create_no_body(self, app_url, headers):
        # Create App
        try:
            result = requests.put(app_url, headers=headers)
            result_code = result.status_code
            assert(result_code == 200 or result_code == 201 or result_code == 204)
            print("Create Test: Pass")
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
            print("Create Failed")

    def test_proxy_user_valid_permissions_create(self, app_url, headers, json_data):
        # Create App
        try:
            result_code = self.put_data(app_url, headers, json_data)
            assert(result_code == 200 or result_code == 201 or result_code == 204)
            print("Create Test: Pass")
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
            print("Create Failed")

    def test_proxy_user_valid_permissions_read(self, app_url, headers):
        # Read App
        try:
            result_code = self.get_data(app_url, headers)
            assert(result_code == 200)
            print("Read Test:   Pass")
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
            print("Read Failed")

    def test_proxy_user_valid_permissions_delete(self, app_url, headers, json_data):
        # Sleep has been added as it takes time for the app to get created
        try:
            time.sleep(5)
            # Delete App
            result_code = self.delete_data(app_url, headers, json_data)
            assert(result_code == 200 or result_code == 204)
            print("Delete Test: Pass\n")
        except (Exception) as e:
            print("The following error occurred: %s" %
                  e, file=sys.stderr)
            print("Delete Failed")

    def test_proxy_unauthorized_user_create(self, app_url, headers):
        result_code = self.put_data(app_url, headers, json_data)
        assert(result_code == 403)
        print("Create Failed: Unauthorized User")

    def test_proxy_unauthorized_user_read(self, app_url, headers):
        # Read App
        result_code = self.get_data(app_url, headers)
        assert(result_code == 403)
        print("Read Failed: Unauthorized User")

    def test_proxy_unauthorized_user_delete(self, app_url, headers):
        result_code = self.delete_data(app_url, headers, json_data)
        assert(result_code == 403)
        print("Delete Failed: Unauthorized User\n")

    def test_invalid_end_points(self, app_url, headers, json_data):
        result_code = self.put_data(app_url, headers, json_data)
        assert(result_code == 403)
        print("Create Failed: Invalid End Point")
