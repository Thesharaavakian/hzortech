#!/bin/bash
set -e

DOMAIN="${DOMAIN:-hzortech.com}"
EMAIL="${CERTBOT_EMAIL:-shara@hzortech.com}"
CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"

mkdir -p /app/logs /var/www/certbot

# Start gunicorn
gunicorn hzortech.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log \
    --log-level info \
    --daemon

# Obtain SSL cert on first boot
if [ ! -f "$CERT_PATH" ]; then
    echo "[startup] No cert found — obtaining via certbot..."
    nginx -c /app/nginx_bootstrap.conf
    certbot certonly --webroot \
        -w /var/www/certbot \
        -d "$DOMAIN" -d "www.$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive
    nginx -s stop
    sleep 1
    echo "[startup] Certificate obtained."
fi

# Schedule renewal (twice daily, standard certbot recommendation)
echo "0 0,12 * * * root certbot renew --quiet --deploy-hook 'nginx -s reload'" \
    > /etc/cron.d/certbot-renew
chmod 644 /etc/cron.d/certbot-renew
service cron start 2>/dev/null || true

exec nginx -g "daemon off;"
