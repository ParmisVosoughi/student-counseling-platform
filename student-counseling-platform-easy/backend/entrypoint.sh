#!/bin/sh
set -e
attempt=0
until python manage.py migrate --noinput; do
  attempt=$((attempt+1))
  if [ "$attempt" -ge 30 ]; then echo "Database migration failed after 30 attempts"; exit 1; fi
  echo "Database not ready yet; retrying..."; sleep 2
done
python manage.py collectstatic --noinput

if [ "${AUTO_SEED_DEMO:-False}" = "True" ] || [ "${AUTO_SEED_DEMO:-False}" = "true" ]; then
  if ! python manage.py shell -c "from accounts.models import User; import sys; sys.exit(0 if User.objects.exists() else 1)"; then
    echo "Empty database detected; creating starter demo data..."
    python manage.py seed_demo
  fi
fi

gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout 60
