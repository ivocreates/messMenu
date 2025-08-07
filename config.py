# MessMenu Rater Configuration

class Config:
    """Base configuration class"""
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    DATABASE = 'messmenu.db'
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Application settings
    ITEMS_PER_PAGE = 20
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Security settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = 'change-this-to-a-random-secret-key-in-production'
    SESSION_COOKIE_SECURE = True

# Default configuration
config = DevelopmentConfig()
