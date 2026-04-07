web: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py ensure_admin && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
