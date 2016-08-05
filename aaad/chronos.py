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
