"""Development settings: verbose errors, permissive hosts, SQLite by default."""

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Django Debug Toolbar style verbosity without the extra dependency:
LOGGING["loggers"]["carepulse"]["level"] = "DEBUG"  # noqa: F405
