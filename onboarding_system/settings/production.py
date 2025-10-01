from .base import *

DEBUG = False

# Production ALLOWED_HOSTS - add your actual domain here
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    # Add your production domain here, e.g.:
    # "yourdomain.com",
    # "www.yourdomain.com",
]

# Additional production settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Database configuration for production
# Make sure to set DATABASE_URL environment variable
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
