#!/usr/bin/python
import utils
import mesos
import os
import sys
import json
import yaml
import re
from quotas import Quotas
import logging

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

class Validator:

    def __init__(self):
        self.messages = []

    def validate(self, act_as, request_uri, action, request_body, framework):
        return self._validate_resource_quotas(act_as, request_uri, action, request_body, framework)

    def _get_requested_details(self, request_body):
        requested = { "instances": 1, "resources": {} }
        try:
            requested['instances'] = int(request_body.get('instances', '1'))
            if 'cpus' in request_body:
                requested['resources']['cpus'] = float(request_body['cpus'])
            if 'mem' in request_body:
                requested['resources']['mem'] = float(request_body['mem'])
            if 'disk' in request_body:
                requested['resources']['disk'] = float(request_body['disk'])
            return requested
        except (Exception) as e:
            logger.exception("Exception -> {} while trying to get requested resources. Request body -> {}".format(str(e), request_body))
            return {}

    def _validate_resource_quotas(self, act_as, request_uri, action, request_body, framework):
        if not action.lower() in [ "put", "post" ] or not Quotas().instance.is_quota_enabled() or not framework.is_quota_validation_required(request_uri):
            return True

        body = None
        try:
            body = json.loads(request_body)
        except (Exception) as e:
            logger.exception("Validation failed because the request body could not be read. Request body: {}".format(request_body))
            self.messages = []
            self.messages.append('Quota validation failed because the request body could not be read - {}.'.format(str(e)))

        requested = self._get_requested_details(body)
        id = framework.get_id(body, request_uri)
        allocated = framework.get_allocation(id)
        logger.debug("Allocated resources from framework {} -> {}".format(framework, allocated))
        instances = requested['instances']
        if not requested['resources']:
            requested['resources'] = allocated['resources']

        if requested['resources'] == allocated['resources'] and requested['instances'] < allocated['instances']:
            # Scale down request
            return True

        quotas = Quotas().instance
        bucket_name = quotas.get_bucket_for_task_name(id)
        resource_quotas = quotas.get_quota_for_bucket(bucket_name)
        total_allocation = quotas.get_task_allocation(bucket_name)
        total_allocated_cpu = total_allocation['resources'].get('cpus', 0.0)
        total_allocated_mem = total_allocation['resources'].get('mem', 0.0)
        total_allocated_disk = total_allocation['resources'].get('disk', 0.0)

        cpu_quota = float(resource_quotas['resources'].get("cpus", 0.0))
        mem_quota = float(resource_quotas['resources'].get("mem", 0.0))
        disk_quota = float(resource_quotas['resources'].get("disk", 0.0))
        requested_cpu = int(requested['instances']) * float(requested['resources'].get('cpus', 0.0))
        requested_mem = int(requested['instances']) * float(requested['resources'].get('mem', 0.0))
        requested_disk = int(requested['instances']) * float(requested['resources'].get('disk', 0.0))
        # Current allocated resources for an app previously deployed.
        allocated_cpu = allocated['instances'] * float(allocated['resources'].get('cpus', 0.0))
        allocated_mem = allocated['instances'] * float(allocated['resources'].get('mem', 0.0))
        allocated_disk = allocated['instances'] * float(allocated['resources'].get('disk', 0.0))
        logger.debug("Requested cpu: {}, allocated_cpu: {}, Total allocated cpu: {}, CPU quota:{}".format(requested_cpu, allocated_cpu, total_allocated_cpu, cpu_quota))
        logger.debug("Requested mem: {}, allocated_mem: {}, Total allocated mem: {}, MEM quota:{}".format(requested_mem, allocated_mem, total_allocated_mem, mem_quota))
        logger.debug("Requested disk: {}, allocated_disk: {}, Total allocated disk: {}, DISK quota:{}".format(requested_disk, allocated_disk, total_allocated_disk, disk_quota))
        valid_quota_request = True
        self.messages = []
        if cpu_quota < (requested_cpu + total_allocated_cpu - allocated_cpu):
            self.messages.append("Requested cpu: {} + total current allocated cpu: {} for user: {} exceeds cpu quota: {}.".format(requested_cpu, (total_allocated_cpu - allocated_cpu), act_as, cpu_quota))
            valid_quota_request = False

        if mem_quota < (requested_mem + total_allocated_mem - allocated_mem):
            self.messages.append("Requested memory: {} + total current allocated memory: {} for user: {} exceeds memory quota: {}.".format(requested_mem, (total_allocated_mem - allocated_mem), act_as, mem_quota))
            valid_quota_request = False

        if disk_quota < (requested_disk + total_allocated_disk - allocated_disk):
            self.messages.append("Requested disk: {} + total current_allocated disk: {} for user: {} exceeds disk quota: {}.".format(requested_disk, (total_allocated_disk - allocated_disk), act_as, disk_quota))
            valid_quota_request = False

        return valid_quota_request
