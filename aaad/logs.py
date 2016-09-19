import logging
from flask import request
from flask_login import current_user

'''
References:
    * https://realpython.com/blog/python/python-web-applications-with-flask-part-iii/
    * http://stackoverflow.com/questions/22868900/how-do-i-safely-get-the-users-real-ip-address-in-flask-using-mod-wsgi
'''

trusted_proxies = {'127.0.0.1'}  # can add more to this if there are several trusted proxies

class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        route = request.access_route + [request.remote_addr]
        remote_addr = next((addr for addr in reversed(route)
                            if addr not in trusted_proxies), request.remote_addr)
        log_record.ip = remote_addr
        log_record.url = request.path
        log_record.method = request.method
        log_record.user_id = current_user.get_id() if current_user.is_authenticated else 'unknown'
        return True
