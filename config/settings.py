from os import getenv
from distutils.util import strtobool


SESSION_LIFETIME = int(getenv('SESSION_LIFETIME'))

URL = getenv('URL')

DEFAULT_IOTA_ADDRESS= getenv('DEFAULT_IOTA_ADDRESS')

AUTHOR_ADDRESSES= bool(strtobool(getenv('AUTHOR_ADDRESSES', 'false')))

NODE_URL = getenv('NODE_URL')

GHOST_ADMIN_KEY = getenv('GHOST_ADMIN_KEY')

ADMIN_PANEL = bool(strtobool(getenv('ADMIN_PANEL', 'false')))