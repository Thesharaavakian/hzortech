# Use official Python image
FROM python:3.13-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies + nginx + certbot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && apt-get update \
 && apt-get install -y nginx certbot python3-certbot-nginx \
 && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy custom nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Expose ports
EXPOSE 80 443

# Make startup script executable
RUN chmod +x /app/run_gunicorn.sh

# Start Gunicorn + Nginx
CMD ["/app/run_gunicorn.sh"]