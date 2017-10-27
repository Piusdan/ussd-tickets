init: python manage.py deploy

web: gunicorn manage:app --preload --reload --workers 5

worker: celery worker -A app.celery_worker.celery -E --without-gossip --without-mingle --without-heartbeat --concurrency=3 --autoscale=10,3 --loglevel=INFO
