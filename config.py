import os
from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).parent.absolute()

    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

    MAX_FILE_SIZE_MB = int(os.environ.get('MAX_FILE_SIZE_MB', 10))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(BASE_DIR / 'uploads')
    CONVERTED_FOLDER = os.environ.get('CONVERTED_FOLDER') or str(BASE_DIR / 'converted')

    ALLOWED_EXTENSIONS = {'xlsx'}

    CLEANUP_INTERVAL_MINUTES = int(os.environ.get('CLEANUP_INTERVAL_MINUTES', 30))
    CLEANUP_AGE_MINUTES = int(os.environ.get('CLEANUP_AGE_MINUTES', 60))

    XLS_MAX_ROWS = 65536
    XLS_MAX_COLS = 256
    XLS_MAX_SHEET_NAME_LENGTH = 31

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
