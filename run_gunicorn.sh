#!/bin/bash
cd /app

# Gunicorn settings
APP_MODULE=hzortech.wsgi:application
BIND_ADDRESS=127.0.0.1:8000
WORKERS=3
TIMEOUT=120

# Logging
mkdir -p /app/logs
ACCESS_LOG=/app/logs/gunicorn_access.log
ERROR_LOG=/app/logs/gunicorn_error.log

# Start Gunicorn in background
gunicorn $APP_MODULE \
    --bind $BIND_ADDRESS \
    --workers $WORKERS \
    --timeout $TIMEOUT \
    --access-logfile $ACCESS_LOG \
    --error-logfile $ERROR_LOG \
    --log-level info &

# Start Nginx in foreground
nginx -g "daemon off;"