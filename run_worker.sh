#!/usr/bin/env bash
celery worker -A app.celery_worker.celery --loglevel=DEBUG --concurrency=20