#!/bin/sh
cd ./foodgram || exit
python manage.py makemigrations;
python manage.py migrate;
python manage.py loaddata Dump.json;
python manage.py collectstatic --noinput;
gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000;