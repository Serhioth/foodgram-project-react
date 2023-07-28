cd foodgram || exit
python manage.py migrate;
python manage.py coolectstatic --noinput;
gunicorn -b 0:8000 foodgram.wsgi
