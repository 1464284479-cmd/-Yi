import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:root@localhost/waste'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME_MINUTES = 10
    PASSWORD_MIN_LENGTH = 8
