import os
BASE_URL = "http://127.0.0.1:8000"
SECRET_KEY = "=r^^(t+_6iu&+d5z=z!nxr^*y4*6!jkw#%u89&p=#58tia446t"
DEBUG = True

# ldap_server
LDAP_SERVER_URL = "ldap://ldap.xiaoneng.cn"

# DB Config
DB_HOST = os.environ.get("HOME_DB_HOST")
DB_NAME = os.environ.get("HOME_DB_NAME")
DB_PASSWORD = os.environ.get("HOME_DB_PWD")
DB_PORT = os.environ.get("HOME_DB_PORT")
DB_USER = os.environ.get("HOME_DB_USER")

# Redis Config
REDIS_DBNUM = 0
REDIS_PORT = os.environ.get("HOME_REDIS_PORT")
REDIS_PASSWORD = os.environ.get("HOME_REDIS_PWD")
REDIS_SERVER = os.environ.get("HOME_REDIS_SERVER")
