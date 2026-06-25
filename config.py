import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
    MYSQL_USER = quote_plus(os.environ.get("MYSQL_USER", ""))
    MYSQL_PASSWORD = quote_plus(os.environ.get("MYSQL_PASSWORD", ""))

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": {
            "ssl": {
                "check_hostname": False
            }
        }
    }