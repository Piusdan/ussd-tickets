web: gunicorn manage:app
worker: celery worker -A app.celery_worker.celery --loglevel=DEBUG
