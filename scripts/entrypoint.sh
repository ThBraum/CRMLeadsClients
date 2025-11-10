#!/bin/sh
set -e

scripts/wait-for-postgresql.sh

python manage.py collectstatic --noinput

echo "Aplicando migrações..."
python manage.py migrate --noinput || true

echo "Iniciando servidor..."
exec "$@"
