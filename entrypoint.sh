#!/bin/ash
if [ "$DATABASE" = "mysql"]
then
    echo "Waiting for mysql"
    while ! nc -z$SQL_HOST $SQL_PORT; do
        sleep 0.1
    done 
        echo "Start mysql successfully"

echo "Apply database migrations"
python manage.py migrate
python manage.py runserver
exec "$@"