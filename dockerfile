FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=topsky.settings

# Ustaw port, jeśli korzystasz z runserver
EXPOSE 8000

CMD ["python", "topsky/manage.py", "runserver", "0.0.0.0:8000"]
