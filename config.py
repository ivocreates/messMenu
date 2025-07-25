# Mess Menu Rater Configuration File

# Database Configuration
DATABASE_URL = 'database/mess_menu.db'

# Flask Configuration
SECRET_KEY = 'mess_menu_rater_secret_key_2025'
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Application Settings
APP_NAME = 'Mess Menu Rater'
ITEMS_PER_PAGE = 10
MAX_RATING = 5
MIN_RATING = 1

# File Upload Settings (for future enhancements)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Email Configuration (for future notifications)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = ''  # Set your email
MAIL_PASSWORD = ''  # Set your email password

# Security Settings
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
WTF_CSRF_ENABLED = True

# Admin Settings
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin123'
DEFAULT_ADMIN_NAME = 'System Administrator'

# Pagination Settings
RATINGS_PER_PAGE = 20
MENU_ITEMS_PER_PAGE = 50

# Cache Settings (for future Redis integration)
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'

# Feature Flags
ENABLE_ORDERS = True
ENABLE_ANALYTICS = True
ENABLE_EMAIL_NOTIFICATIONS = False
ENABLE_USER_PROFILES = False
