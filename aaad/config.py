import os
from datetime import timedelta

SECRET_KEY = os.environ['APP_SECRET_KEY'] # flask
SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'aaadsid') # flask
SESSION_COOKIE_DOMAIN = os.getenv('SESSION_ID_DOMAIN', None) # flask
REMEMBER_COOKIE_NAME = os.environ.get('REMEMBER_COOKIE_NAME', 'aaadrem') # flask-login
REMEMBER_COOKIE_DURATION = timedelta(seconds=int(os.getenv('SESSION_MAXAGE_SECONDS', 120))) # flask-login
REMEMBER_COOKIE_DOMAIN = os.getenv('SESSION_ID_DOMAIN', None) # flask-login
