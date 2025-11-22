import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-sleep-quest'
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    DEBUG = True
