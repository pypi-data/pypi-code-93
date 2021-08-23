import os

__VERSION__ = '0.0.126'
DEBUG = os.environ.get('SAVVIHUB_DEBUG', False)
API_HOST = os.environ.get('SAVVIHUB_API_HOST', 'https://api.savvihub.com')
