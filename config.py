import os

class Config:
    SECRET_KEY = b'+G%\xc0\xae\x13v\xf8O\xb0\xf7\xb6W\xbb\x96\x8a\xdf\xb3\xfa\xa5\x93!'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
