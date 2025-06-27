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

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "topsky.wsgi:application"]
