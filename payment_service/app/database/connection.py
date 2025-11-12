import urllib
from flask_sqlalchemy import SQLAlchemy
from app.core.config import Config

db = SQLAlchemy()

def get_connection_string():
    params = urllib.parse.quote_plus(
        f"DRIVER={{{Config.DB_DRIVER}}};"
        f"SERVER={Config.DB_SERVER},{Config.DB_PORT};"
        f"DATABASE={Config.DB_NAME};"
        f"UID={Config.DB_USER};"
        f"PWD={Config.DB_PASSWORD};"
    )
    return f"mssql+pyodbc:///?odbc_connect={params}"

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_connection_string()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return db
