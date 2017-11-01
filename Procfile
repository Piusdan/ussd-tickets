init: python manage.py reset_db

deploy: python manage.py deploy

web: gunicorn manage:app --preload --reload

worker: celery worker -A app.celery_worker.celery --concurrency=3 --autoscale=10,3 --loglevel=INFO
