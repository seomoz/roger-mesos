#!/usr/bin/python

from __future__ import print_function
import os
import sys
import json
import re
import requests
from framework import Framework
import logging

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

class Marathon(Framework):

    def getName(self):
        return "Marathon"

    def filterResponseBody(self, body, allowed_namespaces, request_uri):
        uri_pattern = re.compile("^{}$".format("/marathon/*v2/apps"))
        uri_match = uri_pattern.match(request_uri)
        if uri_match:
            response = self.filterV2AppsResponse(body, allowed_namespaces)
            return response

        uri_pattern = re.compile("^{}$".format("/marathon/*v2/groups"))
        uri_match = uri_pattern.match(request_uri)
        if uri_match:
            response = self.filterV2GroupsResponse(body, allowed_namespaces)
            return response

        return ""


    def filterV2AppsResponse(self, body, allowed_namespaces):
        filtered_apps = []
        filtered_response = {}
        try:
            data = json.loads(body)
            if 'apps' in data:
                apps = data['apps']
                if not type(apps) == list:
                    return ""

                for app in apps:
                    if 'id' in app:
                        app_id = app['id']
                        for namespace in allowed_namespaces:
                            pattern = re.compile("^{}$".format(namespace))
                            result = pattern.match(app_id)
                            if result:
                                if not app in filtered_apps:
                                    filtered_apps.append(app)
            filtered_response['apps'] = filtered_apps
            return json.dumps(filtered_response)
        except (Exception) as e:
            return ""

    def filterV2GroupsResponse(self, body, allowed_namespaces):
        response = {}
        filtered_apps = []
        filtered_groups = []
        try:
            data = json.loads(body)
            if 'apps' in data.keys():
                filtered_apps = self.filterApps(data['apps'], allowed_namespaces)
            if 'groups' in data:
                filtered_groups = self.filterGroups(data['groups'], allowed_namespaces)

            for item in data.keys():
                if item != 'apps' and item != 'groups':
                    response[item] = data[item]

            response['apps'] = filtered_apps
            response['groups'] = filtered_groups
            return json.dumps(response)
        except (Exception) as e:
            return ""

    def matchPattern(self, id_to_match, allowed_namespaces):
        for namespace in allowed_namespaces:
            pattern = re.compile("^{}$".format(namespace))
            result = pattern.match(id_to_match)
            if result:
                return True
        return False

    def filterApps(self, apps_list, allowed_namespaces):
        allowed_apps = []
        for item in apps_list:
            if 'id' in item:
                app_id = item['id']
                match_app_id = self.matchPattern(app_id, allowed_namespaces)
                if match_app_id and (not item in allowed_apps):
                    allowed_apps.append(item)
        return allowed_apps

    def filterGroups(self, groups_list, allowed_namespaces):
        allowed_groups = []
        for item in groups_list:
           filtered_item = {}
           if 'id' in item:
               group_id = item['id']
               match_group_id = self.matchPattern(group_id, allowed_namespaces)
               if match_group_id and (not item in allowed_groups):
                   allowed_groups.append(item)
               else:            #The id at this level does not match any allowed_namespaces, but a nested id may match
                   filtered_apps = []
                   filtered_groups = []
                   if 'apps' in item and item['apps']:         #Check to see if item['apps'] is not empty
                       filtered_apps = self.filterApps(item['apps'], allowed_namespaces)
                   if 'groups' in item and item['groups']:      #Check to see if item['groups'] is not empty
                       filtered_groups = self.filterGroups(item['groups'], allowed_namespaces)
                   if filtered_apps or filtered_groups:    #Either filtered apps or groups is not empty
                       for elem in item.keys():
                           if elem != 'apps' and elem != 'groups':
                               filtered_item[elem] = item[elem]
                       filtered_item['apps'] = filtered_apps
                       filtered_item['groups'] = filtered_groups
                       allowed_groups.append(filtered_item)

        return allowed_groups

    def get_id(self, request_body, request_uri):
        app_id = None
        try:
            uri_pattern = re.compile("^{}$".format("/marathon/+v2/apps/+.+/.+"))
            uri_match = uri_pattern.match(request_uri)
            if uri_match:     #app_id is in the request_uri, else fetch from request body
                if 'apps' in request_uri:
                    app_id = request_uri[request_uri.rindex("v2/apps/")+8:]
            else:
                app_id = request_body.get('id', None)

            return app_id
        except (Exception) as e:
            logger.exception("Exception -> {}. Failed to get allocated resources from Marathon with request body: {} and request uri:{}".format(str(e), json.dumps(request_body), request_uri))

    def get_allocation(self, id):
        app_id = id
        allocated = { "instances": 0, "resources": { "cpus": 0.0, "mem": 0.0, "disk": 0.0 } }
        try:
            #uri_pattern = re.compile("^{}$".format("/marathon/+v2/apps/+.+/.+"))
            #uri_match = uri_pattern.match(request_uri)
            #if uri_match:     #app_id is in the request_uri, else fetch from request body
            #    if 'apps' in request_uri:
            #        app_id = request_uri[request_uri.rindex("v2/apps/")+8:]
            #else:
            #    app_id = request_body.get('id', None)

            if not app_id:
                return allocated

            marathon_master_url = os.environ['MARATHON_MASTER_URL']
            url = '{}/v2/apps/{}'.format(marathon_master_url.rstrip('/'), app_id)
            resp = requests.get('{}'.format(url))
            if not resp.status_code // 100 == 2:
                return allocated
            data = resp.json()
            if not 'app' in data:
                # Application has not been deployed previously
                return allocated
            data = data['app']
            instances = int(data.get('instances', '0'))
            allocated['instances'] = instances
            resources = {}
            resources['cpus'] = float(data.get('cpus', '0.0'))
            resources['mem'] = float(data.get('mem', '0.0'))
            resources['disk'] = float(data.get('disk', '0.0'))
            allocated['resources'] = resources

            return allocated
        except (Exception) as e:
            logger.exception("Exception -> {}. Failed to get allocated resources from Marathon with app id -> {}.".format(str(e), id))
