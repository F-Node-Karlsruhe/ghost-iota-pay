# -*- coding: utf-8 -*-

import multiprocessing
from os import getenv

from distutils.util import strtobool


bind = getenv('WEB_BIND', '0.0.0.0:8000')
accesslog = '-'
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"  # noqa: E501

workers = int(getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2))
threads = int(getenv('PYTHON_MAX_THREADS', 1))

reload = bool(strtobool(getenv('WEB_RELOAD', 'false')))