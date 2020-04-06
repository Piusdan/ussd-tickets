#!/usr/bin/env bash

# run celery worker

su -m cvs -c "/appenv/bin/celery worker -A app.celery_worker.celery -E \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    --concurrency=3 \
    --autoscale=10,3 \
    --loglevel=INFO"