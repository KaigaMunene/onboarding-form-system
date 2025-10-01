from decouple import config

from .base import *  # noqa F403, F401

if config("ENV_NAME", default="development") == "production":
    from .production import *  # noqa F403, F401
elif config("ENV_NAME", default="development") == "development":
    from .development import *  # noqa F403, F401
