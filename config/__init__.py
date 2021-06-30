from dotenv import load_dotenv
from os import getenv

load_dotenv()

SECRET_KEY = getenv('SECRET_KEY')

DEFAULT_PRICE = int(getenv('PRICE_PER_CONTENT'))

DATABASE_LOCATION = 'sqlite:///data/db.sqlite3'

SESSION_LIFETIME = int(getenv('SESSION_LIFETIME'))

URL = getenv('URL')

DEFAULT_IOTA_ADDRESS= getenv('DEFAULT_IOTA_ADDRESS')

AUTHOR_ADDRESSES= getenv('AUTHOR_ADDRESSES') == 'true'

NODE_URL = getenv('NODE_URL')

GHOST_ADMIN_KEY = getenv('GHOST_ADMIN_KEY')

ADMIN_PANEL = getenv('ADMIN_PANEL') == 'true'