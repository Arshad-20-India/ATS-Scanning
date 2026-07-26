#!/bin/sh
set -e

# RUN_MIGRATIONS defaults to true. docker-compose sets this to "false"
# for the Celery worker service -- only one process should run
# migrations on startup, otherwise two containers starting
# simultaneously (api + worker) could race to apply the same alembic
# revision at once. The API container is the one that owns it.
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

exec "$@"
