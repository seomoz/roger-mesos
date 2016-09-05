#!/usr/bin/python

from __future__ import print_function
import utils
import mesos
import os
import sys
import json
import yaml
import re

quota_file = os.getenv('QUOTA_FILE', '')
master_url = os.getenv('MESOS_MASTER_URL', 'http://localhost:5050')

class Validator:

    def __init__(self):
        self.messages = []

    def validate(self, act_as, action, request_body):
        return self.validate_resource_quotas(act_as, action, request_body)

    def get_requested_resources(self, request_body):
        requested_resources = {}
        try:
            body = json.loads(request_body)
            if 'cpus' in body:
                requested_resources['cpus'] = float(body['cpus'])
            if 'mem' in body:
                requested_resources['mem'] = float(body['mem'])
            if 'disk' in body:
                requested_resources['disk'] = float(body['disk'])

            return requested_resources
        except (Exception) as e:
            return {}

    def validate_resource_quotas(self, act_as, action, request_body):
        if not action.lower() in [ "put", "post" ]:
            return True

        if not quota_file:
            return True

        requested_resources = self.get_requested_resources(request_body)
        tasks = mesos.get_tasks(master_url)
        pattern = re.compile(".*\.{}\..*".format(act_as))
        total_allocated_cpu, total_allocated_mem, total_allocated_disk = (0.0,)*3
        for task in tasks.keys():
            if pattern.match(task):
                total_allocated_cpu += float(tasks[task]['cpus'])
                total_allocated_mem += float(tasks[task]['mem'])
                total_allocated_disk += float(tasks[task]['disk'])
                
        resource_quotas = ""
        resource_quotas = utils.parse_permissions_file(quota_file).get(act_as, {})
        resource_quotas = resource_quotas.get("resources", {})
        cpu_quota = float(resource_quotas.get("cpus", 0.0))
        mem_quota = float(resource_quotas.get("mem", 0.0))
        disk_quota = float(resource_quotas.get("disk", 0.0))
        requested_cpu = float(requested_resources.get("cpus", 0.0))
        requested_mem = float(requested_resources.get("mem", 0.0))
        requested_disk = float(requested_resources.get("disk", 0.0))
        valid_quota_request = True
        self.messages = []
        if cpu_quota < (requested_cpu + total_allocated_cpu):
            self.messages.append("Requested cpu: {} + current allocated cpu:{} for user:{} exceeds cpu quota:{}.".format(requested_cpu, total_allocated_cpu, act_as, cpu_quota))
            valid_quota_request = False

        if mem_quota < (requested_mem + total_allocated_mem):
            self.messages.append("Requested memory: {} + current allocated memory:{} for user:{} exceeds memory quota:{}.".format(requested_mem, total_allocated_mem, act_as, mem_quota))
            valid_quota_request = False

        if disk_quota < (requested_disk + total_allocated_disk):
            self.messages.append("Requested disk: {} + current_allocated disk:{} for user:{} exceeds disk quota:{}.".format(requested_disk, total_allocated_disk, act_as, disk_quota))
            valid_quota_request = False

        return valid_quota_request
