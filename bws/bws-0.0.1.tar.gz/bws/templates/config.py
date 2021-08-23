template = """
# generado automaticamente

import os
import sys
from dotenv import load_dotenv

if "--dev" in sys.argv:
    filenv = "../.env.dev"
    DEBUG = True
else:
    filenv = "../.env"
    DEBUG = False

dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(dotenv_path=os.path.join(dir_path, filenv), verbose=True, override=True)

def parse_url_mysql(user, password, host, port, name):
    return f"mysql+pymysql://{user}:{password}@{host}:{port or 3306}/{name}?charset=UTF8MB4&autocommit=false"


TESTING = False
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", 'development')

NAME     = os.getenv("NAME", "MS")
HOST     = os.getenv("HOST", "localhost")
REGISTER = os.getenv("REGISTER", "https://api.mauja.store")
MS_HOST = os.getenv("MS_HOST")

MYSQL_NAME = os.getenv("MYSQL_NAME")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", parse_url_mysql(
    name=MYSQL_NAME,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    port=MYSQL_PORT,
    host=MYSQL_HOST
))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 490,
    "pool_pre_ping": 60,
}

INSTALLED_APPS = [
    "app.%(app)s",
]
"""