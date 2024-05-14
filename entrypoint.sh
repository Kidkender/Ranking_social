#!/bin/sh

# Wait for the database to be ready
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL is ready!"

# Run Django migrations
python3 manage.py makemigrations
python3 manage.py migrate --noinput

# Import data
python3 manage.py import_data suburbs_10.xlsx

# Collect static files
python3 manage.py collectstatic --noinput --ignore static

# Start Gunicorn
gunicorn ranking_social.wsgi:application --bind 0.0.0.0:8000
