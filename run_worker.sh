#!/usr/bin/env bash
export FLASK_APP=manage.py
export FLASK_DEBUG=1
export MAIL_USERNAME=Cash\ Value\ Solution
export MAIL_PASSWORD=1996tsunami13237
export FLASK_ADMIN=+254703554404
export ADMIN_MAIL=npiusdan@gmail.com
export ADMIN_PHONENUMBER=+254703554404
/appenv/bin/celery worker -A app.celery_worker.celery -B -E \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    --concurrency=3 \
    --autoscale=10,3 \
    --loglevel=INFO