#!/usr/bin/env bash
python manage.py db upgrade && \
gunicorn -b 0.0.0.0:8000 manage:app --workers 5