#!/bin/bash

poetry run python manage.py collectstatic --noinput
poetry run python manage.py migrate
poetry run gunicorn --config deploy/web/gunicorn.conf.py bookkeeper.wsgi
