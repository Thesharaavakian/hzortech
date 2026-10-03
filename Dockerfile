# ── Stage 1: frontend build (Vite) ───────────────────────────────────────
FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Django runtime ──────────────────────────────────────────────
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Vite's own build output (frontend/dist) replaces whatever the build
# context had there, so collectstatic picks up the real, hashed assets.
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Collect static files at build time (whitenoise serves them at runtime)
RUN DJANGO_SECRET_KEY=build-placeholder python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "hzortech.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
