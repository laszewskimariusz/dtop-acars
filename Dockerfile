# Railway deployment Dockerfile
FROM python:3.13-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything except .env file (handled by .dockerignore)
COPY . .

ENV DJANGO_SETTINGS_MODULE=topsky.settings
ENV PYTHONPATH=/app/topsky

# Install Tailwind CSS dependencies
WORKDIR /app/topsky/theme/static_src
RUN npm install

# Build Tailwind CSS
RUN npm run build

# Go back to app directory
WORKDIR /app

# Ustaw port, jeśli korzystasz z runserver
EXPOSE 8000

CMD ["sh", "-c", "cd topsky && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} topsky.wsgi:application"] 