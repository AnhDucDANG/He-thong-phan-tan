import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_PORT = os.getenv("DB_PORT", "1433")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 8004))
