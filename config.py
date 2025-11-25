import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    REDDIS_PORT = os.environ.get("REDDIS_PORT")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    # CACHE_HOST = os.environ.get("CACHE_HOST")
    # CACHE_PORT = os.environ.get("CACHE_PORT")
    DATA_FROM = os.environ.get("DATA_FROM")
    DATA_TO = os.environ.get("DATA_TO")
    INPUT_QUEUE = os.environ.get("INPUT_QUEUE")
