from os import getenv
from distutils.util import strtobool


SESSION_LIFETIME = int(getenv('SESSION_LIFETIME', 24))

URL = getenv('URL', 'http://localhost:2368')

DEFAULT_IOTA_ADDRESS= getenv('DEFAULT_IOTA_ADDRESS')

DEFAULT_PRICE = int(getenv('PRICE_PER_CONTENT', 1000000))

AUTHOR_ADDRESSES= bool(strtobool(getenv('AUTHOR_ADDRESSES', 'false')))

NODE_URL = getenv('NODE_URL', 'https://api.hornet-1.testnet.chrysalis2.com')

GHOST_ADMIN_KEY = getenv('GHOST_ADMIN_KEY')

ADMIN_PANEL = bool(strtobool(getenv('ADMIN_PANEL', 'false')))