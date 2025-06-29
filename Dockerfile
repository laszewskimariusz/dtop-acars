# Railway deployment Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything except .env file (handled by .dockerignore)
COPY . .

ENV DJANGO_SETTINGS_MODULE=topsky.settings
ENV PYTHONPATH=/app/topsky

# Ustaw port, jeśli korzystasz z runserver
EXPOSE 8000

# Use gunicorn with better logging for Railway
CMD ["sh", "-c", "cd topsky && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 --access-logfile - --error-logfile - --log-level debug --preload topsky.wsgi:application"] 