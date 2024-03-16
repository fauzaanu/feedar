from gunicorn import workers

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "radheefu.com",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
CSRF_TRUSTED_ORIGINS = [
    "https://radheefu.com",
]
CSRF_COOKIE_DOMAIN = "radheefu.com"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ["PGDATABASE"],
        'USER': os.environ["PGUSER"],
        'PASSWORD': os.environ["PGPASSWORD"],
        'HOST': os.environ["PGHOST"],
        'PORT': os.environ["PGPORT"],
    }
}

# Cache settings
# https://docs.djangoproject.com/en/5.0/topics/cache/#setting-up-the-cache
# These are the default values for Railway's Redis cache
# REDIS_PRIVATE_URL=redis://default:${{REDIS_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:6379
# REDIS_URL=redis://default:${{REDIS_PASSWORD}}@${{RAILWAY_TCP_PROXY_DOMAIN}}:${{RAILWAY_TCP_PROXY_PORT}}

REDIS_URL = os.environ["REDIS_PRIVATE_URL"]
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": [
            REDIS_URL,  # primary
            # "redis://127.0.0.1:6378",  # read-replica 1
            # "redis://127.0.0.1:6377",  # read-replica 2
        ],
        "KEY_PREFIX": "radheefu_com",
    }
}

# setup logging
# https://docs.djangoproject.com/en/5.0/topics/logging/
import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}

from huey import RedisHuey
from redis import ConnectionPool

pool = ConnectionPool()
HUEY = RedisHuey(SITE_NAME, connection_pool=pool.from_url(REDIS_URL))
