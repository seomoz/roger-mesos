#!/usr/bin/python

from __future__ import print_function
import os
import sys
from abc import ABCMeta, abstractmethod

class Framework(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def filterResponseBody(self, body, allowed_namespaces, request_uri):
        pass

    @abstractmethod
    def get_allocation(self, request_body, request_uri):
        pass

