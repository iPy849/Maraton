import os

class Config:
    SECRET_KEY = 'proyecto_bda_merida_secret_key'


class DevelopmentConfig(Config):
    DEBUG = True