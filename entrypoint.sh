#!/bin/ash
if [ "$DATABASE" = "mysql"]
then
    echo "Waiting for mysql"
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done 
        echo "Start mysql successfully"

echo "Make new migrations"
python3 manage.py makemigrations

echo "Apply database migrations"
python3 manage.py migrate --noinput

echo "Apply import data from excel"
python3 manage.py import_data suburbs_10.xlsx

echo "Collect static files"
python3 manage.py collectstatic --noinput --ignore static

echo "Start server" 
python manage.py runserver --bind 0.0.0.0:8000"

exec "$@"