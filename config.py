import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'rf-tower-mapper-dev-key')
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATA_DIR, 'towers.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# OpenCelliD
OPENCELLID_API_KEY = os.environ.get('OPENCELLID_API_KEY', '')
OPENCELLID_BASE_URL = 'https://opencellid.org/cell'
OPENCELLID_DAILY_LIMIT = 1000
OPENCELLID_CACHE_HOURS = 24

# US MCC codes
US_MCC_CODES = [310, 311, 312, 313, 316]

# Search defaults
DEFAULT_RADIUS_KM = 10
MAX_RADIUS_KM = 50
MIN_RADIUS_KM = 1
