#!/usr/bin/env bash

if [ "$1" != "" ] && [ "$1" == "web" ]; then
  echo "-----> Running webserver"
  echo "-----> Migrating database"
  python manage.py migrate
  echo "-----> Collecting static assets"
  python manage.py collectstatic --noinput

  echo "-----> Starting gunicorn server"
  exec gunicorn nightcrawler.wsgi --log-file=- --bind=0.0.0.0:8000
fi

if [ "$1" != "" ] && [ "$1" == "worker" ]; then
  echo "-----> Running worker"
  exec python manage.py rqworker high default low
fi