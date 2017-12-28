#!/usr/bin/env bash

# create pid and log files
mkdir -p /var/run/celery
mkdir -p /var/log/celery

celery worker -A app.celery_worker.celery -B -E \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    --concurrency=3 \
    --autoscale=10,3 \
    --loglevel=INFO