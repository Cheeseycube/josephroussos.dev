# app.wsgi

import sys
import logging
from dotenv import load_dotenv

sys.path.insert(0, '/var/www/josephroussos.dev')
sys.path.insert(0, '/var/www/josephroussos.dev/venv/lib/python3.10/site-packages/')

load_dotenv('/var/www/josephroussos.dev/.env')
ChessDB.makeConnectionPool(4)

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
from app import app as application