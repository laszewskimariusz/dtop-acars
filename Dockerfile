# Railway deployment Dockerfile
FROM python:3.13-slim

# Install Node.js, npm and curl
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything except .env file (handled by .dockerignore)
COPY . .

ENV DJANGO_SETTINGS_MODULE=topsky.settings
ENV PYTHONPATH=/app/topsky

# Install Tailwind CSS dependencies and build
WORKDIR /app/topsky/theme/static_src
RUN npm install
RUN npm run build

# Go back to app directory
WORKDIR /app

# Create static directory if it doesn't exist
RUN mkdir -p /app/topsky/theme/static/css/dist

# Ustaw port, jeśli korzystasz z runserver
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

CMD ["sh", "-c", "cd topsky && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile - topsky.wsgi:application"] 