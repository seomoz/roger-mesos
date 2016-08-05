#!/usr/bin/python

from __future__ import print_function
import os
import sys
from abc import ABCMeta, abstractmethod

class Framework(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def filterBody(self, body, allowed_namespaces, request_uri):
        pass

