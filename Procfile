web: newrelic-admin run-program gunicorn backend.wsgi -b 0.0.0.0:$PORT -w 2 --log-file -
worker: celery -A backend worker -B -l info -c 2
