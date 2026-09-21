web: python manage.py migrate --noinput && python manage.py seed_data && python manage.py collectstatic --noinput && gunicorn TaskAss.wsgi --bind 0.0.0.0:$PORT
