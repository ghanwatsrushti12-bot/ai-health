release: python manage.py migrate --no-input
web: gunicorn -c gunicorn.conf.py carepulse.wsgi:application
