deploy: python manage.py deploy

web: gunicorn manage:app --reload

worker: celery worker -A app.celery_worker.celery -B -E --without-gossip --without-mingle --without-heartbeat --concurrency=3 --autoscale=10,3 --loglevel=INFO
