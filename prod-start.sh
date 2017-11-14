#!/usr/bin/env bash

# wait for PSQL server to start
sleep 10

echo "running post deployment tasks"

# run migartion and deployment tasks
su -m cvs -c "python manage.py deploy"
echo "Done!"
echo "Serving app"
# run the application server with 5 workers in sync
su -m cvs -c "gunicorn -b 0.0.0.0:8000 \
manage:app \
--preload \
--reload \
--workers 5"