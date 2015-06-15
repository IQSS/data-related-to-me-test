from __future__ import absolute_import
import json
import sys
from os import makedirs
from os.path import join, normpath, isdir, isfile

from .base import *

SECRET_KEY = '6i^f=ha-hahp(tm_$jk4sltim8%jl2b)o5$e!2i*!&m4kvrg#w'

LOCAL_SETUP_DIR = join(BASE_DIR, 'test_setup')
if not isdir(LOCAL_SETUP_DIR):
    makedirs(LOCAL_SETUP_DIR)

DATABASES = {
    'xdefault': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(LOCAL_SETUP_DIR, 'dataverse.sqlite3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dvndb',
        'USER': 'dvnapp',
        'PASSWORD': '123',
        'HOST': 'localhost'
    }
}


SESSION_COOKIE_NAME = 'mydata_local'

# where static files are collected
STATIC_ROOT = join(LOCAL_SETUP_DIR, 'static')
if not isdir(STATIC_ROOT):
    makedirs(STATIC_ROOT)
