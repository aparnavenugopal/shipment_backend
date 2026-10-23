import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host = os.getenv("DB_HOST","127.0.0.1"),
        port = int(os.getenv("DB_PORT", "3306")),
        user = os.environ["DB_USER"],
        password = os.environ["DB_PASSWORD"],
        database = os.environ["DB_NAME"],
    )
