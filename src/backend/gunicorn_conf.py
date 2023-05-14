import os

from uvicorn.workers import UvicornWorker

# Server settings
bind = "0.0.0.0:8080"
backlog = 2048  # default
proc_name = None  # default

# Worker settings
worker_class = UvicornWorker
workers = int(os.getenv("GUNICORN_WORKERS", "1"))
worker_connections = 1000  # default
threads = 1  # default
timeout = 900
graceful_timeout = 30  # default
keepalive = 2  # default

# Server mechanics settings
daemon = False  # default
pidfile = None  # default
umask = 0  # default
user = None
group = None
tmp_upload_dir = None  # default

# Log settings
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
errorlog = os.getenv("GUNICORN_ERROR_LOGFILE", "-")  # '-' to stderr
accesslog = os.getenv("GUNICORN_ACCESS_LOGFILE", "-")  # '-' to stdout

# SSL settings
# if need, gunicorn can be configured for https
