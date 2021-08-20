

class Config():
    SECRET_KEY = 'lrse4tse4tse4tsfj123456789'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

    # flask session configuration
    SESSION_TYPE = 'sqlalchemy'
    
