#!/usr/bin/python

from __future__ import print_function
import unittest
import os
import socket
import argparse
import json
import sys
import httplib
import urllib
import requests
import base64
import subprocess
import time
import pdb
import getopt

def post_data(url,headers,payload):
    result = requests.post(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)

def get_data(url,headers,payload):
    url = url+payload['id']
    result = requests.get(url,data=payload,headers=headers)
    return result.status_code

def put_data(url,headers,payload):
    url = url+payload['id']
    result = requests.put(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)

def delete_data(url,headers,payload):
    url = url+payload['id']
    result = requests.delete(url, data=json.dumps(payload), headers=headers)
    return (result.status_code)

'''def store_original_remote_file(remote_path,host):
    try:
        user = os.getlogin()
        subprocess.call(['scp', ':'.join([host,remote_path]),'/tmp'])
    except:
        print("Failed to store original file from remote server")'''

'''def scp_to_remote_location(filepath,remote_path,machine_list,shared_flag):
    try:
        user = os.getlogin()
        # If shared flag set , copy to one machine else copy to all machines
        if shared_flag == True:
          subprocess.call(['scp', filepath, ':'.join([machine_list[0],remote_path])])
        else:
          for host in machine_list:
            subprocess.call(['scp', filepath, ':'.join([host,remote_path])])
    except:
        print("Failed to copy permissions file to remote location")'''

def test_create_app_with_no_headers(environment):

  create_pass = False
  try:

    app_url = 'http://'+environment+':8080/v2/apps'
    with open("auth-poc-prod-test-app.json") as json_file:
         json_data = json.load(json_file)
    headers = { "Content-Type": "application/json" }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert (result_code != 201)
    print("Create Test: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code != 200)
    print("Read Test:   Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code != 200)
    print("Update Test: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code != 200)
    print("Delete Test: Pass\n")

  except:

    print("\nTest Case : Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def test_user_crud_on_root(environment):

  create_pass = False
  try:

    app_url = 'http://'+environment+':4080/marathon/v2/apps'

    with open("auth-poc-prod-test-app.json") as json_file:
         json_data = json.load(json_file)

    # Creating Authorization for header using Base64 encoding (username:password)
    encoded = base64.b64encode(b'admin:admin')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert(result_code == 201)
    print("Create Test: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Read Test:   Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Update Test: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Delete Test: Pass\n")

  except:
    print("\nTest Case Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def test_user_ben_on_dev(environment):

  create_pass = False
  try:

    app_url = 'http://'+environment+':8080/v2/apps'
    with open("auth-poc-dev-test-app.json") as json_file:
         json_data = json.load(json_file)

    # Creating Authorization for header using Base64 encoding (username:password)
    encoded = base64.b64encode(b'ben:ben')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert(result_code == 201)
    print("Create Test: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Read Test:   Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Update Test: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Delete Test: Pass\n")

  except:
    print("\nTest Case Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def test_user_mac_dev_shared_with_ben(environment):

  create_pass = False
  try:

    app_url = 'http://'+environment+':8080/v2/apps'
    with open("auth-poc-dev-shared-test-app.json") as json_file:
         json_data = json.load(json_file)

    # Creating Authorization for header using Base64 encoding (username:password)
    encoded = base64.b64encode(b'mac:mac')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert(result_code == 201)
    print("Create Test: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Read Test:   Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Update Test: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Delete Test: Pass\n")

  except:
    print("\nTest Case Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def test_user_tom_on_dev(environment):

  create_pass = False
  try:

    app_url = 'http://'+environment+':8080/v2/apps'
    with open("auth-poc-dev-test-app.json") as json_file:
         json_data = json.load(json_file)

    # Creating Authorization for header using Base64 encoding (username:password)
    encoded = base64.b64encode(b'tom:tom')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert(result_code == 201)
    print("Create Test: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Read Test:   Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Update Test: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Delete Test: Pass\n")

  except:
    print("\nTest Case Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def test_user_sam_dev_shared_with_ben(environment,permissions_file):

  create_pass = False
  try:

    app_url = 'http://'+environment+':4080/v2/apps'
    #with open("auth-poc-dev-shared-test-app.json") as json_file:
    #     json_data = json.load(json_file)

    with open(permissions_file) as json_file:
         json_data = json.load(json_file)

    # Creating Authorization for header using Base64 encoding (username:password)
    encoded = base64.b64encode(b'sam:sam')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert(result_code == 201)
    print("Create Test: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Read Test:   Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Update Test: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    assert(result_code == 200)
    print("Delete Test: Pass\n")

  except:
    print("\nTest Case Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def test_user_crud_in_unauthorized_environment(environment):

  create_pass = False
  try:

    app_url = 'http://'+environment+':8080/v2/apps'
    with open("auth-poc-prod-test-app.json") as json_file:
         json_data = json.load(json_file)

    # Creating Authorization for header using Base64 encoding (username:password)
    encoded = base64.b64encode(b'mac:mac')
    encoded = "Basic " + encoded
    headers = { "Content-Type": "application/json", "Authorization" : encoded }

    # Create App
    result_code = post_data(app_url,headers,json_data)
    assert(result_code != 201)
    print("Create Test: Not Allowed to Create -- Result: Pass")
    create_pass = True

    # Read App
    result_code = get_data(app_url,headers,json_data)
    assert(result_code != 200)
    print("Read Test: Not Allowed to Read     -- Result: Pass")

    # Update App
    result_code = put_data(app_url,headers,json_data)
    assert(result_code != 200)
    print("Update Test: Not Allowed to Update -- Result: Pass")

    # Delete App
    result_code = delete_data(app_url,headers,json_data)
    print("Delete Test: Not Allowed to Delete -- Result: Pass\n")

  except:
    print("\nTest Case Failed")
    # Cleanup the app if the create had passed
    if create_pass == True:
       encoded = base64.b64encode(b'admin:admin')
       encoded = "Basic " + encoded
       headers = { "Content-Type": "application/json", "Authorization" : encoded }
       result_code = delete_data(app_url,headers,json_data)

def main(args):

    if len(args) < 3:
        print("Please provide list of machines and location of permission file, then retry.\nExiting...")
        sys.exit(0)

    permissions_file = args[len(args)-1]
    #shared_flag = False
    #optlist, args = getopt.getopt(sys.argv[1:], 's:',['shared-storage='])

    #if len(optlist) > 0:
    #  if str(optlist[0][1]) == 'yes':
    #    shared_flag = True

    #machine_list = args[0:(len(args)-1)]

    machine = args[(len(args)-2)]

    print("\n {} {}".format(permissions_file, machine))

    # Check if the environment is up and reachable
    port = 4080
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((machine, port))
    sock.settimeout(1)

    if result == 0:
        print("\nEnvironemnt {}: Reachable".format(machine))
        sock.close()
    else:
        print ("\nEnvironment {}: Unreachable".format(machine))
        sock.close()

    # Store original file from remote server to local /tmp
    #store_original_remote_file(remote_file_path,machine_list[0])

    print ("\nExecuting Tests for environment :",machine)
    #scp_to_remote_location("user-permissions.json",remote_file_path,machine_list,shared_flag)
    #time.sleep(10)

    print("\nExecuting Test: User with Root Access:\n")
    test_user_crud_on_root(machine, permissions_file)
    '''print("\nExecuting Test: User with No Access:\n")
    test_create_app_with_no_headers(machine)
    print("\nExecuting Test: User with Dev Access:\n")
    test_user_ben_on_dev(machine)
    print("\nExecuting Test: User with Shared Directory Access:\n")
    test_user_mac_dev_shared_with_ben(machine)
    print("\nExecuting Test: CRUD on Unauthorized Environment:\n")
    test_user_crud_in_unauthorized_environment(machine)

    print("We will modify the user permissions and rerun.")

    scp_to_remote_location("user-permissions-negative.json",remote_file_path,machine_list,shared_flag)
    time.sleep(10)

    print("\nExecuting Test: Old User with Dev Access:(Should Fail)")
    test_user_ben_on_dev(machine)
    print("\nExecuting Test: Old User with Shared Directory Access:(Should Fail)")
    test_user_mac_dev_shared_with_ben(machine)
    print("\nExecuting Test: New User with Dev Access:")
    test_user_tom_on_dev(machine)
    print("\nExecuting Test: New User with Shared Directory Access:\n")
    test_user_sam_dev_shared_with_ben(machine)

    #Replace back original file to server
    scp_to_remote_location("/tmp/user-permissions.json",remote_file_path,machine_list,shared_flag)
    os.system("rm /tmp/user-permissions.json")'''


if __name__ == "__main__":
    main(sys.argv)
