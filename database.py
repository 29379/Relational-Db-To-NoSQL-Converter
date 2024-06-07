import psycopg2
import pymongo


POSTGRE_CONFIG = {
    "dbname": "zbd_czy_dojade",
    "user": "postgres",
    "password": "asdlkj000",
    "host": "localhost",
    "port": "5432",
}

OUTPUT_PATH = "resources/diagram.png"


def create_connection():
    conn = psycopg2.connect(**POSTGRE_CONFIG)
    return conn


def get_sqlalchemy_uri():
    return f"postgresql+psycopg2://{POSTGRE_CONFIG['user']}:{POSTGRE_CONFIG['password']}@{POSTGRE_CONFIG['host']}:{POSTGRE_CONFIG['port']}/{POSTGRE_CONFIG['dbname']}"


def mongo_database():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    return client["zbd_czy_dojade"]
