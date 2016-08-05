#!/usr/bin/python

from __future__ import print_function
import os
import sys
import re
from marathon import Marathon
from chronos import Chronos


class FrameworkUtils:

    def getFramework(self, request_uri):
        marathon_pattern = re.compile("^{}$".format("/marathon/.*"))
        marathon_check = marathon_pattern.match(request_uri)
        chronos_pattern = re.compile("^{}$".format("/chronos/.*"))
        chronos_check = chronos_pattern.match(request_uri)
        if marathon_check:
            return Marathon()
        elif chronos_check:
            return Chronos()
        else:
            return None
