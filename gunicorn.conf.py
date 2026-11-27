"""Gunicorn configuration for production deployment.

Usage:
    gunicorn -c gunicorn.conf.py carepulse.wsgi:application
"""

import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
timeout = 60
graceful_timeout = 30
keepalive = 5

accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Restart workers periodically to guard against memory leaks.
max_requests = 1000
max_requests_jitter = 50
