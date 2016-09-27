#!/usr/bin/python

from __future__ import print_function
import os
import sys
import json
import re
from framework import Framework

class Chronos(Framework):

    def getName(self):
        return "Chronos"

    def filterResponseBody(self, body, allowed_namespaces, request_uri):
        filtered_response = []
        try:
            jobs = json.loads(body)
            for job in jobs:
                if 'name' in job:
                    job_name = job['name']
                    for namespace in allowed_namespaces:
                        pattern = re.compile("^{}$".format(namespace))
                        result = pattern.match(job_name)
                        if result:
                            if not job in filtered_response:
                                filtered_response.append(job)
            return json.dumps(filtered_response)
        except (Exception) as e:
            return ""

    def get_id(self, request_body, request_uri):
        job_name = None
        try:
            uri_pattern = re.compile("^{}$".format("/chronos/+scheduler/(iso8601|dependency)/*"))
            uri_match = uri_pattern.match(request_uri)
            if uri_match:     #job_name for chronos is always in the request body
                job_name = request_body['name']

            return job_name
        except (Exception) as e:
            logger.exception("Failed to get id from Chronos with request body: {} and request uri:{}".format(json.dumps(request_body), request_uri))

    def get_allocation(self, id):
        job_name = id
        allocated = { "instances": 0, "resources": { "cpus": 0.0, "mem": 0.0, "disk": 0.0 } }
        try:
            if not job_name:
                return allocated

            chronos_master_url = os.environ['CHRONOS_MASTER_URL']
            url = '{}/scheduler/jobs'.format(chronos_master_url.rstrip('/'))
            resp = requests.get('{}'.format(url))
            if not resp.status_code // 100 == 2:
                return allocated
            jobs = resp.json()
            resources = {}
            for job in jobs:
                if job['name'] == job_name:
                    resources['cpus'] = float(job.get('cpus', '0.0'))
                    resources['mem'] = float(job.get('mem', '0.0'))
                    resources['disk'] = float(job.get('disk', '0.0')) 
                    break
            allocated['instances'] = 1    # Always 1 for Chronos jobs
            allocated['resources'] = resources

            return allocated
        except (Exception) as e:
            logger.exception("Failed to get allocated resources from Chronos with job name -> {} in request body".format(id))
