#!/bin/sh
cd ./foodgram || exit
python manage.py makemigrations;
python manage.py migrate;
python manage.py loaddata Dump.json;
echo "Data loaded succesfully"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'pass1234')" |\
    python manage.py shell
echo "Superuser created successfully"
python manage.py collectstatic --noinput;
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000;