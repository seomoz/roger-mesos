#!/usr/bin/python

from __future__ import print_function
import os
import sys
import json
import re
from framework import Framework

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

