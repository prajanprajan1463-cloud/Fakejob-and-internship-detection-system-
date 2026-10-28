import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
basedir = Path(__file__).resolve().parent
load_dotenv(basedir / '.env')


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-fallback-secret-key-replace-in-production'
    
    # Database configuration with support for postgres:// compatibility
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    if not database_url and os.environ.get('VERCEL'):
        # On Vercel serverless, /tmp is the only writable directory
        SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/fake_job_detection.db"
    else:
        SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{(basedir / 'instance' / 'fake_job_detection.db').as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Request limits
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB max upload/request body
    
    # Security & Sessions
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # Valid for session duration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 86400))  # 1 day
    
    # Risk Scoring Thresholds
    RISK_THRESHOLD_LOW = int(os.environ.get('RISK_THRESHOLD_LOW', 30))
    RISK_THRESHOLD_HIGH = int(os.environ.get('RISK_THRESHOLD_HIGH', 60))
    
    # ML Model directory
    ML_MODEL_DIR = basedir / 'ml' / 'artifacts'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration with in-memory database."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app) if hasattr(Config, 'init_app') else None
        # In production, ensure SECRET_KEY is set securely
        if cls.SECRET_KEY == 'dev-fallback-secret-key-replace-in-production':
            import warnings
            warnings.warn("SECRET_KEY environment variable is not set! Using fallback in production is insecure.")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

