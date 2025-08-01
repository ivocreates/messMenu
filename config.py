"""
Flask Configuration for Mess Menu Rater
Theme Colors: #186F65, #B5CB99, #FCE09B, #B2533E
"""

import os

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mess-menu-rater-secret-key-2025'
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'mess_menu.db')
    
    # Application Settings
    DEBUG = True
    TESTING = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    
    # File Upload (for future menu item images)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    
    # Theme Colors
    THEME_COLORS = {
        'primary': '#186F65',      # Dark Green/Teal
        'secondary': '#B5CB99',    # Light Green
        'accent': '#FCE09B',       # Light Yellow/Cream
        'tertiary': '#B2533E',     # Terracotta/Brown
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6'
    }
    
    # Pagination
    ITEMS_PER_PAGE = 12
    
    # Default Admin Credentials
    DEFAULT_ADMIN = {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@messmenu.com',
        'full_name': 'System Administrator'
    }

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
