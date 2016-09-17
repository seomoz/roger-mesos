import logging
from flask import request
from flask_login import current_user

'''
References:
    * https://realpython.com/blog/python/python-web-applications-with-flask-part-iii/
'''

class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        log_record.url = request.path
        log_record.method = request.method
        log_record.ip = request.environ.get("REMOTE_ADDR")
        log_record.user_id = current_user.get_id() if current_user.is_authenticated else 'unknown'
        return True
