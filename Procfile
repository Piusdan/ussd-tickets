deploy: python manage.py deploy

web: gunicorn manage:app --reload

worker: celery worker -A app.celery_worker.celery --loglevel=INFO
