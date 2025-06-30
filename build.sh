#!/usr/bin/env bash
# install dependencies
pip install -r requirements.txt

# apply migrations automatically
python manage.py migrate

# collect static files (optional, but useful)
python manage.py collectstatic --noinput
