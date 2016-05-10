import os


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/starmap.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class _Production(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('STARMAP_DATABASE_URI')


Production = _Production()