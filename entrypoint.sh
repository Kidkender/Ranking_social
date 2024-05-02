#!/bin/ash
if [ "$DATABASE" = "mysql"]
then
    echo "Waiting for mysql"
    while ! nc -z$SQL_HOST $SQL_PORT; do
        sleep 0.1
    done 
        echo "Start mysql successfully"
echo "Make new migrations"
python manage.py makemigrations

echo "Apply database migrations"
python manage.py migrate

echo "Apply import data from excel"
python manage.py import_data suburbs_3.xlsx

echo "Start server" 
python manage.py runserver

exec "$@"